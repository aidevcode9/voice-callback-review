"""Offline behavior with synthetic development text and controlled local HTTP responses."""

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from hashlib import sha256
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from test_ollama import server

from voice_callback.classify import (
    MAX_TRANSCRIPT_BYTES,
    PROMPT_VERSION,
    build_classification_request,
    classify,
    load_transcript,
    validate_decision,
)
from voice_callback.cli import main
from voice_callback.domain import (
    CallbackDecision,
    FailureCode,
    Outcome,
    RunFailure,
    RunSuccess,
    TranscriptOrigin,
    TranscriptVersion,
)
from voice_callback.models import load_registry
from voice_callback.ollama import OllamaClient, OllamaError
from voice_callback.storage import render_run, save_run

ROOT = Path(__file__).resolve().parents[1]
MODEL = load_registry(ROOT / "config/models.json")[0]
TEXT = "Caller: Please call me back about my appointment."


def decision(**changes):
    return {
        "label": "callback_required",
        "rule_ids": ["CB-002"],
        "reason": "The caller requests a callback.",
        "evidence": ["Please call me back"],
        **changes,
    }


def fixtures():
    return {
        "/api/version": (200, {"version": "0.40.15"}, 0),
        "/api/tags": (200, {"models": [{"name": MODEL.model_id, "digest": "sha256:abc"}]}, 0),
        "/api/show": (
            200,
            {
                "details": {"format": "gguf", "family": "qwen35"},
                "model_info": {"general.architecture": "qwen35", "qwen35.context_length": 262144},
                "capabilities": ["completion", "thinking"],
                "thinking": {"values": [False, True], "default": True},
            },
            0,
        ),
        "/api/chat": (
            200,
            {
                "model": MODEL.model_id,
                "done": True,
                "done_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps(decision())},
            },
            0,
        ),
    }


class PromptCompatibility(unittest.TestCase):
    def test_packaged_v2_keeps_existing_system_and_request_hashes(self):
        transcript = TranscriptVersion(
            "prompt-compat",
            "v1",
            "Caller: café 東京. Please call me back.\nRepresentative: Noted.",
            TranscriptOrigin.TEXT,
        )
        request = build_classification_request(
            transcript, MODEL, (ROOT / "docs/CALLBACK_POLICY.md").read_bytes()
        )
        self.assertEqual(PROMPT_VERSION, "callback-text-v2")
        self.assertEqual(
            request.prompt_sha256,
            "fc0507692c9b15de6ee1cc928475f808c29723a3d6611d28b736c3e9f432e107",
        )
        self.assertEqual(
            request.request_sha256,
            "14a8b592a577ae20dc29d411ca9f2abac6fdf932213a3f5d4811597363dc46d0",
        )


class ClassificationBehavior(unittest.TestCase):
    def setUp(self):
        self.transcript = TranscriptVersion("DEV-SYNTHETIC", "v1", TEXT, TranscriptOrigin.TEXT)

    def run_classifier(self, routes=None, transcript=None, model=MODEL):
        bodies = []
        with server(fixtures() if routes is None else routes, bodies) as (url, requests):
            result = classify(
                transcript or self.transcript,
                model,
                OllamaClient(url),
                policy_path=ROOT / "docs/CALLBACK_POLICY.md",
            )
        return result, requests, bodies

    def test_success_has_exact_evidence_identity_hashes_and_explicit_request_controls(self):
        result, requests, bodies = self.run_classifier()
        assert isinstance(result, RunSuccess)
        assert isinstance(result.output, CallbackDecision)
        self.assertEqual(result.output.label, Outcome.CALLBACK_REQUIRED)
        self.assertEqual(result.output.evidence, ("Please call me back",))
        self.assertEqual(result.provenance.model_digest, "sha256:abc")
        self.assertEqual(result.provenance.transcript_sha256, self.transcript.text_sha256)
        self.assertEqual(result.provenance.case_id, self.transcript.case_id)
        self.assertEqual(result.provenance.runtime_version, "0.40.15")
        self.assertEqual(len(result.provenance.policy_sha256 or ""), 64)
        self.assertEqual(len(result.provenance.prompt_sha256 or ""), 64)
        self.assertEqual(len(result.provenance.request_sha256 or ""), 64)
        self.assertGreaterEqual(result.provenance.elapsed_seconds, 0)
        self.assertEqual(
            requests,
            [
                ("GET", "/api/version"),
                ("GET", "/api/tags"),
                ("POST", "/api/show"),
                ("POST", "/api/chat"),
                ("GET", "/api/tags"),
            ],
        )
        request = bodies[1]
        self.assertFalse(request["truncate"])
        self.assertFalse(request["shift"])
        self.assertFalse(request["think"])
        self.assertFalse(request["stream"])
        self.assertEqual(request["keep_alive"], 0)
        self.assertEqual(request["options"]["num_ctx"], 8192)
        self.assertEqual(json.loads(request["messages"][1]["content"]), {"transcript": TEXT})
        self.assertIn("FINAL known conversation state", request["messages"][0]["content"])
        self.assertIn("CB-003", request["messages"][0]["content"])

    def test_empty_and_oversized_transcripts_fail_before_any_network(self):
        for text in (" \n", "x" * (MAX_TRANSCRIPT_BYTES + 1), "Ã©" * MAX_TRANSCRIPT_BYTES):
            with self.subTest(size=len(text)):
                result, requests, _ = self.run_classifier(
                    transcript=replace(self.transcript, text=text)
                )
                self.assertIsInstance(result, RunFailure)
                assert isinstance(result, RunFailure)
                self.assertEqual(result.failure.code, FailureCode.INVALID_INPUT)
                self.assertEqual(requests, [])
                self.assertFalse(hasattr(result, "output"))

    def test_missing_prompt_asset_is_safe_configuration_failure_without_network(self):
        with patch("voice_callback.classify.files", side_effect=FileNotFoundError("private-path")):
            result, requests, _ = self.run_classifier()
        self.assertIsInstance(result, RunFailure)
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)
        self.assertIn("prompt", result.failure.message)
        self.assertNotIn("private-path", render_run(result))
        self.assertEqual(requests, [])

    def test_invalid_settings_and_changed_policy_fail_without_network(self):
        for settings in (
            {},
            {**MODEL.settings, "think": True},
            {**MODEL.settings, "num_ctx": True},
            {**MODEL.settings, "temperature": float("nan")},
            {**MODEL.settings, "keep_alive": 1},
        ):
            with self.subTest(settings=settings):
                result, requests, _ = self.run_classifier(model=replace(MODEL, settings=settings))
                assert isinstance(result, RunFailure)
                self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)
                self.assertEqual(requests, [])
        with patch("voice_callback.classify.Path.read_bytes", return_value=b"changed"):
            result, requests, _ = self.run_classifier()
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)
        self.assertEqual(requests, [])

    def test_missing_and_remote_models_never_call_inference_or_download(self):
        for models in ([], [{"name": MODEL.model_id, "digest": "abc", "remote_host": "remote"}]):
            routes = fixtures()
            routes["/api/tags"] = (200, {"models": models}, 0)
            result, requests, _ = self.run_classifier(routes)
            self.assertIsInstance(result, RunFailure)
            self.assertEqual(len(requests), 2)
            self.assertFalse(hasattr(result, "output"))

    def test_metadata_and_old_runtime_are_rejected_before_inference(self):
        for change in (
            {"remote_model": "remote"},
            {"capabilities": []},
            {"thinking": {"values": [True]}},
            {"model_info": {"general.architecture": "qwen35", "qwen35.context_length": 100}},
        ):
            routes = fixtures()
            routes["/api/show"] = (200, {**routes["/api/show"][1], **change}, 0)
            result, requests, _ = self.run_classifier(routes)
            assert isinstance(result, RunFailure)
            self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)
            self.assertNotIn(("POST", "/api/chat"), requests)
        routes = fixtures()
        routes["/api/version"] = (200, {"version": "0.40.14"}, 0)
        result, requests, _ = self.run_classifier(routes)
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)
        self.assertNotIn(("POST", "/api/chat"), requests)

    def test_bad_model_output_is_failure_with_no_success_label(self):
        for content in (
            "not json",
            json.dumps(decision(evidence=["fabricated"])),
            json.dumps(decision(rule_ids=["NC-001"])),
        ):
            routes = fixtures()
            routes["/api/chat"][1]["message"]["content"] = content
            result, requests, _ = self.run_classifier(routes)
            assert isinstance(result, RunFailure)
            self.assertEqual(result.failure.code, FailureCode.INVALID_OUTPUT)
            self.assertNotIn("output", json.loads(render_run(result))["run"])
            self.assertEqual(requests.count(("POST", "/api/chat")), 1)

    def test_partial_length_wrong_identity_and_tool_responses_fail(self):
        for change in (
            {"done": False},
            {"done_reason": "length"},
            {"model": "different"},
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(decision()),
                    "tool_calls": [{}],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(decision()),
                    "thinking": "hidden trace",
                }
            },
        ):
            routes = fixtures()
            routes["/api/chat"] = (200, {**routes["/api/chat"][1], **change}, 0)
            result, _, _ = self.run_classifier(routes)
            assert isinstance(result, RunFailure)
            self.assertEqual(result.failure.code, FailureCode.INVALID_OUTPUT)

    def test_http_memory_context_and_missing_model_are_safe_typed_failures(self):
        for status, message, code in (
            (500, "CUDA out of memory private data", FailureCode.GPU_MEMORY),
            (500, "input exceeds context length private data", FailureCode.INVALID_INPUT),
            (
                400,
                "request (9361 tokens) exceeds the available context size (2048 tokens), try increasing it",
                FailureCode.INVALID_INPUT,
            ),
            (404, "private data", FailureCode.MODEL_MISSING),
            (500, "private data", FailureCode.HTTP_ERROR),
        ):
            routes = fixtures()
            routes["/api/chat"] = (status, {"error": message}, 0)
            result, _, _ = self.run_classifier(routes)
            assert isinstance(result, RunFailure)
            self.assertEqual(result.failure.code, code)
            self.assertNotIn("private data", render_run(result))

    def test_inference_deadline_size_limit_and_no_retry(self):
        routes = fixtures()
        routes["/api/chat"] = (*routes["/api/chat"][:2], 0.15)
        with server(routes) as (url, requests):
            result = classify(self.transcript, MODEL, OllamaClient(url, inference_timeout=0.04))
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.TIMEOUT)
        self.assertEqual(requests.count(("POST", "/api/chat")), 1)
        routes = fixtures()
        routes["/api/chat"] = (200, {"padding": "x" * 2000}, 0)
        with server(routes) as (url, _):
            result = classify(self.transcript, MODEL, OllamaClient(url, max_response_bytes=1000))
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.INVALID_RESPONSE)
        for timeout in (0, float("nan"), 601):
            with self.assertRaises(ValueError):
                OllamaClient(inference_timeout=timeout)

    def test_model_change_during_run_is_not_success(self):
        routes = fixtures()
        with server(routes) as (url, _):
            client = OllamaClient(url)
            inventory = client.installed_models()
            with patch.object(client, "installed_models", side_effect=[inventory, ()]):
                result = classify(self.transcript, MODEL, client)
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.CONFIGURATION)

    def test_runtime_failure_keeps_prepared_prompt_and_input_provenance(self):
        routes = fixtures()
        routes["/api/version"] = (503, {"error": "private server detail"}, 0)
        result, requests, _ = self.run_classifier(routes)
        assert isinstance(result, RunFailure)
        self.assertEqual(result.failure.code, FailureCode.HTTP_ERROR)
        self.assertEqual(result.provenance.runtime_version, "unknown")
        self.assertEqual(len(result.provenance.prompt_sha256 or ""), 64)
        self.assertEqual(len(result.provenance.request_sha256 or ""), 64)
        self.assertEqual(result.provenance.transcript_sha256, self.transcript.text_sha256)
        self.assertEqual(requests, [("GET", "/api/version")])
        self.assertNotIn("private server detail", render_run(result))

    def test_new_text_and_settings_keep_prior_provenance_unchanged(self):
        first, _, _ = self.run_classifier()
        second, _, _ = self.run_classifier(
            transcript=replace(self.transcript, version_id="v2", text=TEXT + "\n"),
            model=replace(MODEL, settings={**MODEL.settings, "seed": 43}),
        )
        self.assertNotEqual(first.provenance.run_id, second.provenance.run_id)
        self.assertNotEqual(first.provenance.transcript_sha256, second.provenance.transcript_sha256)
        self.assertNotEqual(first.provenance.request_sha256, second.provenance.request_sha256)
        self.assertEqual(first.provenance.prompt_sha256, second.provenance.prompt_sha256)
        self.assertEqual(first.provenance.model.settings["seed"], 42)


class DecisionValidation(unittest.TestCase):
    def test_three_outcomes_and_all_rules_accept_exact_supporting_quotes(self):
        for label, rules in (
            ("callback_required", ["UR-001", "CB-002", "CB-003"]),
            ("no_callback", ["NC-001", "NC-002", "NC-003"]),
            ("needs_review", ["NR-001"]),
        ):
            output = validate_decision(json.dumps(decision(label=label, rule_ids=rules)), TEXT)
            self.assertEqual(output.label.value, label)

    def test_unknown_rules_wrong_labels_empty_fields_extra_keys_and_nonexact_quotes_rejected(self):
        for change in (
            {"label": "maybe"},
            {"rule_ids": ["CB-999"]},
            {"rule_ids": ["NC-001"]},
            {"rule_ids": []},
            {"rule_ids": ["CB-002", "CB-002"]},
            {"reason": " "},
            {"reason": "x" * 1201},
            {"evidence": []},
            {"evidence": [""]},
            {"evidence": ["please call me back"]},
            {"evidence": ["Please call me back"] * 6},
            {"extra": "x"},
        ):
            with self.subTest(change=change), self.assertRaises(OllamaError):
                validate_decision(json.dumps(decision(**change)), TEXT)
        with self.assertRaises(OllamaError):
            validate_decision('{"label":"no_callback",' + json.dumps(decision())[1:], TEXT)


class InputStorageCLI(unittest.TestCase):
    def setUp(self):
        (ROOT / ".test-work").mkdir(exist_ok=True)
        folder = tempfile.TemporaryDirectory(dir=ROOT / ".test-work")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.input = self.folder / "call.txt"
        self.input.write_bytes((TEXT + "\r\n").encode())

    def invoke(self, *extra):
        output = StringIO()
        args = [
            "classify",
            "--input",
            str(self.input),
            "--case-id",
            "DEV",
            "--model",
            MODEL.id,
            "--output-dir",
            str(self.folder / "runs"),
            "--inference-lock-dir",
            str(self.folder / "admission"),
            *extra,
        ]
        with redirect_stdout(output), redirect_stderr(StringIO()):
            code = main(args)
        return code, json.loads(output.getvalue())

    def test_txt_retains_exact_newlines_and_input_only_jsonl_selects_one_case(self):
        transcript = load_transcript(self.input, "DEV")
        self.assertEqual(transcript.text, TEXT + "\r\n")
        path = self.folder / "input.jsonl"
        path.write_text(json.dumps({"case_id": "DEV", "transcript": TEXT}), encoding="utf-8")
        self.assertEqual(load_transcript(path, "DEV", "v2").version_id, "v2")
        for value in (
            {"case_id": "DEV", "transcript": TEXT, "expected_label": "no_callback"},
            {"case_id": "DEV"},
            {"case_id": "DEV", "transcript": 3},
        ):
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_transcript(path, "DEV")
        path.write_text(
            "\n".join([json.dumps({"case_id": "DEV", "transcript": TEXT})] * 2), encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            load_transcript(path, "DEV")

    def test_jsonl_preserves_unicode_separators_and_exact_transcript_hash(self):
        path = self.folder / "input.jsonl"
        for separator in ("\u0085", "\u2028", "\u2029"):
            text = f"Caller: Please call me back{separator}about my appointment."
            rows = [
                json.dumps({"case_id": "OTHER", "transcript": "Another call."}),
                json.dumps({"case_id": "DEV", "transcript": text}, ensure_ascii=False),
            ]
            for delimiter in ("\n", "\r\n"):
                for final_newline in (False, True):
                    with self.subTest(
                        separator=ascii(separator),
                        delimiter=ascii(delimiter),
                        final_newline=final_newline,
                    ):
                        raw = (delimiter.join(rows) + (delimiter if final_newline else "")).encode(
                            "utf-8"
                        )
                        path.write_bytes(raw)
                        transcript = load_transcript(path, "DEV")
                        self.assertEqual(transcript.text, text)
                        self.assertEqual(
                            transcript.text_sha256, sha256(text.encode("utf-8")).hexdigest()
                        )

    def test_invalid_encoding_missing_id_and_oversized_file_fail(self):
        for content in (b"\xff", b"x" * (1024 * 1024 + 1)):
            self.input.write_bytes(content)
            with self.assertRaises(ValueError):
                load_transcript(self.input, "DEV")
        with self.assertRaises(ValueError):
            load_transcript(self.input, "")
        with self.assertRaises(ValueError):
            load_transcript(self.folder / "absent.txt", "DEV")

    def test_cli_saves_success_and_failure_exclusively_with_json_stdout(self):
        with server(fixtures()) as (url, _):
            code, output = self.invoke("--url", url)
        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "success")
        files = list((self.folder / "runs").glob("*.json"))
        self.assertEqual(json.loads(files[0].read_text(encoding="utf-8")), output)
        self.input.write_text(" ", encoding="utf-8")
        code, output = self.invoke()
        self.assertEqual(code, 1)
        self.assertEqual(output["status"], "processing_error")
        self.assertNotIn("output", output["run"])
        self.assertEqual(len(list((self.folder / "runs").glob("*.json"))), 2)
        transcript = load_transcript(self.input, "DEV")
        result = classify(transcript, MODEL, OllamaClient())
        path = save_run(result, self.folder)
        original = path.read_bytes()
        with self.assertRaises(FileExistsError):
            save_run(result, self.folder)
        self.assertEqual(path.read_bytes(), original)

    def test_cli_configuration_and_storage_failures_have_nonzero_exits(self):
        code, output = self.invoke("--model", "unknown")
        self.assertEqual(code, 2)
        self.assertEqual(output["status"], "configuration_error")
        with patch("voice_callback.cli.save_run", side_effect=OSError):
            self.input.write_text(" ", encoding="utf-8")
            code, output = self.invoke()
        self.assertEqual(code, 1)
        self.assertEqual(output["status"], "storage_error")
        with self.assertRaises(SystemExit) as caught, redirect_stderr(StringIO()):
            main(["classify", "--input", str(self.input), "--case-id", "DEV"])
        self.assertEqual(caught.exception.code, 2)
