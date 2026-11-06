"""Boundary behavior that can regress when replacing explicit checks with Pydantic."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from pydantic import ValidationError

from voice_callback.classify import (
    PROMPT_VERSION,
    build_classification_request,
    decision_schema,
    parse_transcripts,
    validate_decision,
)
from voice_callback.contracts import (
    PREDICTION_RECORD,
    RUN_RECORD,
    CallbackOutput,
    ClassifierSettings,
    ModelRegistry,
    validate_contract,
    validate_record,
)
from voice_callback.domain import (
    CallbackDecision,
    Failure,
    FailureCode,
    JsonValue,
    Outcome,
    RunFailure,
    RunProvenance,
    RunSuccess,
    Stage,
    TranscriptOrigin,
    TranscriptVersion,
)
from voice_callback.evaluation_contracts import InferenceComplete
from voice_callback.json_io import parse_json
from voice_callback.models import load_registry
from voice_callback.ollama import OllamaError
from voice_callback.storage import render_run, write_json

ROOT = Path(__file__).resolve().parents[1]
MODEL = load_registry(ROOT / "config/models.json")[0]
OUTPUT = {
    "label": "callback_required",
    "rule_ids": ["CB-002"],
    "reason": "The caller requests follow-up.",
    "evidence": ["Call me back."],
}


class StrictContractBehavior(unittest.TestCase):
    def test_json_settings_reject_coercion_boolean_numbers_and_extras(self):
        settings: dict[str, JsonValue] = dict(MODEL.settings)
        accepted = validate_contract(ClassifierSettings, settings)
        self.assertEqual(accepted.num_ctx, 8192)
        for changes in (
            {"num_ctx": "8192"},
            {"num_ctx": True},
            {"num_ctx": 8192.0},
            {"temperature": False},
            {"temperature": "0"},
            {"temperature": float("inf")},
            {"seed": "42"},
            {"think": 0},
            {"think": "false"},
            {"think": True},
            {"keep_alive": False},
            {"keep_alive": "0"},
            {"unexpected": 1},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_contract(ClassifierSettings, {**settings, **changes})

    def test_registry_version_is_integer_and_nested_contracts_forbid_extra_fields(self):
        raw = (ROOT / "config/models.json").read_text(encoding="utf-8")
        registry = parse_json(raw)
        assert isinstance(registry, dict)
        for version in (True, "1", 1.0, 2):
            with self.subTest(version=version), self.assertRaises(ValueError):
                validate_contract(ModelRegistry, {**registry, "schema_version": version})
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-work") as folder:
            path = Path(folder) / "models.json"
            for content in (
                raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                raw.replace('"temperature": 0', '"temperature": 1e400'),
                raw.replace('"temperature": 0', '"temperature": null'),
                raw.replace('"settings": {', '"extra": true, "settings": {', 1),
            ):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_registry(path)

    def test_generated_schema_is_used_for_the_request_and_prompt(self):
        schema = decision_schema()
        self.assertEqual(schema, CallbackOutput.model_json_schema())
        self.assertFalse(schema["additionalProperties"])
        required = schema["required"]
        assert isinstance(required, list)
        self.assertEqual(set(required), set(OUTPUT))
        properties = schema["properties"]
        assert isinstance(properties, dict)
        for name, maximum in (("rule_ids", 7), ("evidence", 5)):
            field = properties[name]
            assert isinstance(field, dict)
            self.assertEqual((field["minItems"], field["maxItems"]), (1, maximum))
            self.assertTrue(field["uniqueItems"])
        transcript = TranscriptVersion("DEV", "v1", "Call me back.", TranscriptOrigin.TEXT)
        request = build_classification_request(transcript, MODEL, b"Development policy.")
        self.assertEqual(request.body["format"], schema)
        messages = request.body["messages"]
        assert isinstance(messages, list) and isinstance(messages[0], dict)
        self.assertIn(json.dumps(schema, sort_keys=True), str(messages[0]["content"]))
        self.assertEqual(PROMPT_VERSION, "callback-text-v2")

    def test_output_validation_preserves_semantic_guards_and_unicode(self):
        for separator in ("\u0085", "\u2028", "\u2029"):
            text = "Caller:" + separator + "Call me back."
            payload = {**OUTPUT, "evidence": [text]}
            decision = validate_decision(json.dumps(payload, ensure_ascii=False), text)
            self.assertEqual(decision.evidence, (text,))
            records = parse_transcripts(
                json.dumps({"case_id": "DEV", "transcript": text}, ensure_ascii=False).encode()
            )
            self.assertEqual(records[0].text, text)
        for changes in (
            {"label": 1},
            {"rule_ids": "CB-002"},
            {"evidence": [1]},
            {"evidence": ["Call me back.", "Call me back."]},
            {"reason": " \t\n"},
            {"rule_ids": ["CB-002", "CB-002"]},
            {"rule_ids": ["NC-001"]},
            {"evidence": ["Invented quote."]},
            {"extra": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(OllamaError):
                validate_decision(json.dumps({**OUTPUT, **changes}), "Call me back.")

    def test_run_and_prediction_variants_never_mix_failure_and_success(self):
        provenance = RunProvenance(
            "synthetic-run",
            Stage.CLASSIFICATION,
            MODEL,
            "synthetic-digest",
            "0.40.15",
            "v1",
            "a" * 64,
            "callback-text-v1",
            "b" * 64,
            "1.0",
            "c" * 64,
            "2026-11-06T00:00:00+00:00",
            0.1,
            case_id="DEV",
        )
        output = CallbackDecision(
            Outcome.CALLBACK_REQUIRED, ("CB-002",), OUTPUT["reason"], ("Call me back.",)
        )
        success = json.loads(render_run(RunSuccess(provenance, output)))
        failure = json.loads(
            render_run(RunFailure(provenance, Failure(FailureCode.TIMEOUT, "Timed out.")))
        )
        self.assertEqual(
            RUN_RECORD.validate_json(json.dumps(success)).run.provenance.prompt_version,
            "callback-text-v1",
        )
        for invalid in (
            {**success, "status": "processing_error"},
            {**failure, "status": "success"},
            {**success, "extra": True},
            {**success, "run": {**success["run"], "failure": failure["run"]["failure"]}},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                RUN_RECORD.validate_json(json.dumps(invalid), strict=True)
        with self.assertRaises(ValueError):
            render_run(RunSuccess(replace(provenance, elapsed_seconds=-1), output))
        identity = {
            "case_id": "DEV",
            "transcript_sha256": "a" * 64,
            "run_id": "synthetic-run",
            "run_sha256": "d" * 64,
        }
        for invalid in (
            {**identity, "status": "success", "failure": failure["run"]["failure"]},
            {**identity, "status": "processing_error", "output": OUTPUT},
            {**identity, "status": "success", "output": OUTPUT, "label": "no_callback"},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                PREDICTION_RECORD.validate_json(json.dumps(invalid), strict=True)

    def test_invalid_completion_cannot_create_a_file_or_coerce_counts(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-work") as folder:
            path = Path(folder) / "inference-complete.json"
            record = {
                "schema_version": 1,
                "evaluation_id": "synthetic",
                "count": True,
                "system_sha256": "a" * 64,
                "predictions_sha256": "b" * 64,
            }
            with self.assertRaises(ValueError):
                write_json(path, record, InferenceComplete)
            self.assertFalse(path.exists())

    def test_python_whitespace_semantics_are_preserved_without_normalizing_text(self):
        for control in ("\u001c", "\u001d", "\u001e", "\u001f"):
            with self.subTest(control=ord(control)):
                with self.assertRaises(OllamaError):
                    validate_decision(json.dumps({**OUTPUT, "reason": control}), "Call me back.")
                with self.assertRaises(ValueError):
                    parse_transcripts(json.dumps({"case_id": control, "transcript": "x"}).encode())
                raw = (ROOT / "config/models.json").read_text(encoding="utf-8")
                value = json.loads(raw)
                value["models"][0]["id"] = "abc" + control + "def"
                with self.assertRaises(ValueError):
                    validate_contract(ModelRegistry, value)
        output = validate_decision(
            json.dumps({**OUTPUT, "reason": "  Follow-up.  "}), "Call me back."
        )
        self.assertEqual(output.reason, "  Follow-up.  ")

    def test_validation_messages_do_not_echo_untrusted_values(self):
        secret = "UNTRUSTED_TRANSCRIPT_VALUE"
        with self.assertRaises(ValueError) as caught:
            validate_record(PREDICTION_RECORD, {"status": secret, "transcript": secret})
        self.assertNotIn(secret, str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            validate_contract(CallbackOutput, {secret: secret})
        self.assertNotIn(secret, str(caught.exception))
