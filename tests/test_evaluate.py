"""Scoring arithmetic and artifact isolation with synthetic data and a local-runtime fake."""

import json
import tempfile
import unittest
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from voice_callback.cli import main
from voice_callback.datasets import load_answers, load_split, object_value
from voice_callback.domain import CallbackDecision, Failure, FailureCode, JsonValue, Outcome
from voice_callback.evaluate import evaluate, freeze_run, read_document, score_run
from voice_callback.evaluation_contracts import EvaluationReport, InferenceComplete
from voice_callback.json_io import parse_json, parse_jsonl
from voice_callback.models import load_registry
from voice_callback.ollama import InstalledModel, OllamaClient, OllamaError
from voice_callback.scoring import Prediction, ReferenceAnswer, score

ROOT = Path(__file__).resolve().parents[1]
MODEL = next(row for row in load_registry(ROOT / "config/models.json") if row.id == "qwen35-4b")
RULE = {
    Outcome.CALLBACK_REQUIRED: "CB-002",
    Outcome.NO_CALLBACK: "NC-001",
    Outcome.NEEDS_REVIEW: "NR-001",
}


def decision(label):
    return CallbackDecision(label, (RULE[label],), "Synthetic decision.", ("Please call me back",))


class FakeOllama(OllamaClient):
    def __init__(self, results=None, on_chat: Callable[[], None] | None = None):
        super().__init__()
        self.results = list(results or [Outcome.CALLBACK_REQUIRED, Outcome.NO_CALLBACK])
        self.requests = []
        self.on_chat = on_chat
        self.digest = "synthetic-model-digest"
        self.metadata_revision = 0

    def version(self) -> str:
        return "0.40.15"

    def installed_models(self) -> tuple[InstalledModel, ...]:
        return (InstalledModel(MODEL.model_id, self.digest),)

    def show(self, model_id: str) -> dict[str, JsonValue]:
        return {
            "details": {"format": "gguf", "family": "qwen35"},
            "capabilities": ["completion", "thinking"],
            "thinking": {"values": [False, True]},
            "model_info": {"general.architecture": "qwen35", "qwen35.context_length": 262144},
            "synthetic_revision": self.metadata_revision,
        }

    def chat(self, request: dict[str, JsonValue]) -> dict[str, JsonValue]:
        self.requests.append(request)
        if self.on_chat is not None:
            self.on_chat()
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        if isinstance(result, FailureCode):
            raise OllamaError(result, "Synthetic processing failure.")
        output = decision(result)
        return {
            "model": MODEL.model_id,
            "done": True,
            "done_reason": "stop",
            "message": {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "label": output.label.value,
                        "rule_ids": list(output.rule_ids),
                        "reason": output.reason,
                        "evidence": list(output.evidence),
                    }
                ),
            },
        }


class ScoringBehavior(unittest.TestCase):
    def test_exact_counts_include_review_unsafe_misses_and_failures(self):
        expected = (
            [Outcome.CALLBACK_REQUIRED] * 4 + [Outcome.NO_CALLBACK] * 2 + [Outcome.NEEDS_REVIEW] * 2
        )
        observed = [
            Outcome.CALLBACK_REQUIRED,
            Outcome.NEEDS_REVIEW,
            Outcome.NO_CALLBACK,
            None,
            Outcome.CALLBACK_REQUIRED,
            Outcome.NO_CALLBACK,
            Outcome.NEEDS_REVIEW,
            None,
        ]
        answers = tuple(
            ReferenceAnswer(str(i), label, "Reference.") for i, label in enumerate(expected)
        )
        predictions = tuple(
            Prediction(
                str(i),
                "hash",
                str(uuid4()),
                decision(label) if label else Failure(FailureCode.TIMEOUT, "Timed out."),
            )
            for i, label in enumerate(observed)
        )
        result = score(predictions, answers)
        self.assertEqual((result.total, result.valid_outputs, result.correct_outputs), (8, 6, 3))
        self.assertEqual(
            result.metrics["strict_callback_recall"],
            {"numerator": 1, "denominator": 4, "value": 0.25},
        )
        self.assertEqual(
            result.metrics["callback_precision"], {"numerator": 1, "denominator": 2, "value": 0.5}
        )
        self.assertEqual(
            result.metrics["needs_review_rate"], {"numerator": 2, "denominator": 8, "value": 0.25}
        )
        self.assertEqual(result.metrics["valid_output_coverage"]["value"], 0.75)
        self.assertEqual(result.unsafe_misses, ("2",))
        self.assertEqual(
            result.processing_failures_by_expected,
            {"callback_required": 1, "no_callback": 0, "needs_review": 1},
        )
        self.assertEqual(result.failure_codes, {"timeout": 2})
        self.assertEqual(
            result.confusion_matrix["callback_required"],
            {"callback_required": 1, "no_callback": 1, "needs_review": 1},
        )
        self.assertEqual(len(result.disagreements), 5)

    def test_undefined_denominators_are_null_and_all_failure_recall_is_zero(self):
        empty = score((), ())
        self.assertTrue(all(metric["value"] is None for metric in empty.metrics.values()))
        failure = Prediction("A", "hash", "run", Failure(FailureCode.TIMEOUT, "Timeout."))
        result = score((failure,), (ReferenceAnswer("A", Outcome.CALLBACK_REQUIRED, "Reference."),))
        self.assertEqual(result.metrics["strict_callback_recall"]["value"], 0)
        self.assertIsNone(result.metrics["callback_precision"]["value"])
        self.assertEqual(result.metrics["valid_output_coverage"]["denominator"], 1)
        no_callback = score((failure,), (ReferenceAnswer("A", Outcome.NO_CALLBACK, "Reference."),))
        self.assertIsNone(no_callback.metrics["strict_callback_recall"]["value"])

    def test_missing_duplicate_and_foreign_predictions_are_rejected(self):
        answer = ReferenceAnswer("A", Outcome.CALLBACK_REQUIRED, "Reference.")
        prediction = Prediction("A", "hash", "run", decision(Outcome.CALLBACK_REQUIRED))
        for predictions, answers in (
            ((), (answer,)),
            ((prediction, prediction), (answer,)),
            ((prediction,), (answer, answer)),
            ((prediction,), (ReferenceAnswer("B", answer.label, "Reference."),)),
        ):
            with self.subTest(predictions=predictions), self.assertRaises(ValueError):
                score(predictions, answers)


class EvaluationArtifacts(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        folder = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.dataset = self.folder / "gold"
        self.output = self.folder / "reports"
        (self.dataset / "inputs").mkdir(parents=True)
        (self.dataset / "answers").mkdir()
        manifest = {
            "dataset_version": "synthetic-v1",
            "status": "frozen",
            "splits": {},
            "files": {},
        }
        for split, prefix in (("development", "D"), ("evaluation", "H")):
            ids = [prefix + "1", prefix + "2"]
            manifest["splits"][split] = ids
            rows = [
                {
                    "case_id": case_id,
                    "transcript": f"Caller: Synthetic {case_id}.\u2028Please call me back.",
                }
                for case_id in ids
            ]
            answers = [
                {
                    "case_id": case_id,
                    "expected_label": label.value,
                    "rationale": "ANSWER_ONLY_DEV",
                    "rule_ids": [RULE[label]],
                    "evidence": ["Please call me back"],
                }
                for case_id, label in zip(
                    ids, (Outcome.CALLBACK_REQUIRED, Outcome.NO_CALLBACK), strict=True
                )
            ]
            for part, values in (("inputs", rows), ("answers", answers)):
                raw = (
                    "\n".join(json.dumps(row, ensure_ascii=False) for row in values) + "\n"
                ).encode("utf-8")
                name = f"{part}/{split}.jsonl"
                (self.dataset / name).write_bytes(raw)
                manifest["files"][name] = {"sha256": sha256(raw).hexdigest()}
        self.manifest = self.dataset / "manifest.json"
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")

    def run_evaluation(self, client=None, **kwargs):
        return evaluate(
            self.dataset,
            "development",
            MODEL,
            client or FakeOllama(),
            output_root=self.output,
            policy_path=ROOT / "docs/CALLBACK_POLICY.md",
            **kwargs,
        )

    def clean_git(self, args, **kwargs):
        return "f" * 40 + "\n" if args[1] == "rev-parse" else ""

    def test_answers_open_only_after_all_predictions_are_closed_and_saved(self):
        handles = []
        original_open = Path.open

        def track_open(path, *args, **kwargs):
            handle = original_open(path, *args, **kwargs)
            if path.name == "predictions.jsonl" and args and args[0] == "x":
                handles.append(handle)
            return handle

        client = FakeOllama()

        def read_answers(dataset):
            self.assertEqual(len(client.requests), 2)
            self.assertTrue(handles and all(handle.closed for handle in handles))
            directory = next(self.output.iterdir())
            self.assertTrue((directory / "inference-complete.json").is_file())
            return load_answers(dataset)

        with (
            patch.object(Path, "open", autospec=True, side_effect=track_open),
            patch("voice_callback.evaluate.load_answers", side_effect=read_answers) as answers,
        ):
            client.on_chat = lambda: self.assertEqual(answers.call_count, 0)
            directory = self.run_evaluation(client)
        report = read_document(directory / "report.json", EvaluationReport)
        scored = object_value(report["score"])
        self.assertEqual(scored["total"], 2)
        self.assertEqual(scored["correct_outputs"], 2)
        self.assertEqual(len(list((directory / "runs").glob("*.json"))), 2)
        self.assertNotIn("ANSWER_ONLY_DEV", json.dumps(client.requests))
        self.assertIn(
            "\u2028", json.loads(client.requests[0]["messages"][1]["content"])["transcript"]
        )

    def test_offline_rescoring_is_identical_without_inference_or_rewriting(self):
        client = FakeOllama()
        directory = self.run_evaluation(client)
        original = (directory / "report.json").read_bytes()
        first = score_run(directory, self.dataset)
        second = score_run(directory, self.dataset)
        self.assertEqual(first, second)
        self.assertEqual((directory / "report.json").read_bytes(), original)
        self.assertEqual(len(client.requests), 2)

    def test_processing_failure_is_in_denominators_and_not_a_policy_prediction(self):
        directory = self.run_evaluation(FakeOllama([FailureCode.TIMEOUT, Outcome.NO_CALLBACK]))
        report = object_value(read_document(directory / "report.json", EvaluationReport)["score"])
        metrics = object_value(report["metrics"])
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["valid_outputs"], 1)
        self.assertEqual(object_value(metrics["strict_callback_recall"])["value"], 0)
        self.assertEqual(object_value(metrics["valid_output_coverage"])["value"], 0.5)
        failure = json.loads((directory / "predictions.jsonl").read_text().split("\n")[0])
        self.assertNotIn("output", failure)
        with self.assertRaises(ValueError):
            freeze_run(directory, self.dataset)

    def test_interrupted_run_retains_partial_artifacts_without_opening_answers(self):
        with (
            patch(
                "voice_callback.evaluate.load_answers", side_effect=AssertionError("Answers opened")
            ),
            self.assertRaises(KeyboardInterrupt),
        ):
            self.run_evaluation(FakeOllama([Outcome.CALLBACK_REQUIRED, KeyboardInterrupt()]))
        directory = next(self.output.iterdir())
        self.assertTrue((directory / "aborted.json").is_file())
        self.assertEqual(len(parse_jsonl((directory / "predictions.jsonl").read_bytes())), 1)
        self.assertFalse((directory / "report.json").exists())
        with self.assertRaises(OSError):
            score_run(directory, self.dataset)

    def test_configuration_drift_aborts_before_answers_or_report(self):
        client = FakeOllama()
        client.on_chat = lambda: setattr(client, "metadata_revision", 1)
        with (
            patch(
                "voice_callback.evaluate.load_answers", side_effect=AssertionError("Answers opened")
            ),
            self.assertRaises(ValueError),
        ):
            self.run_evaluation(client)
        directory = next(self.output.iterdir())
        self.assertTrue((directory / "aborted.json").is_file())
        self.assertFalse((directory / "inference-complete.json").exists())

    def test_prediction_run_and_input_tampering_are_rejected_before_answers(self):
        for artifact in ("predictions.jsonl", "inputs.jsonl", "run"):
            with self.subTest(artifact=artifact):
                directory = self.run_evaluation()
                target = (
                    next((directory / "runs").glob("*.json"))
                    if artifact == "run"
                    else directory / artifact
                )
                target.write_bytes(target.read_bytes() + b" ")
                with (
                    patch(
                        "voice_callback.evaluate.load_answers",
                        side_effect=AssertionError("Answers opened"),
                    ),
                    self.assertRaises(ValueError),
                ):
                    score_run(directory, self.dataset)

    def test_foreign_or_incomplete_predictions_rejected_even_when_file_hash_is_updated(self):
        directory = self.run_evaluation()
        path = directory / "predictions.jsonl"
        rows = parse_jsonl(path.read_bytes())
        path.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
        ready = read_document(directory / "inference-complete.json", InferenceComplete)
        ready["predictions_sha256"] = sha256(path.read_bytes()).hexdigest()
        (directory / "inference-complete.json").write_text(json.dumps(ready), encoding="utf-8")
        with self.assertRaises(ValueError):
            score_run(directory, self.dataset)

    def test_differing_existing_report_is_preserved(self):
        directory = self.run_evaluation()
        path = directory / "report.json"
        path.write_text('{"different": true}', encoding="utf-8")
        with self.assertRaises(ValueError):
            score_run(directory, self.dataset)
        self.assertEqual(path.read_text(), '{"different": true}')

    def test_malformed_prediction_status_is_a_validation_error(self):
        for status in ([], {}):
            directory = self.run_evaluation()
            path = directory / "predictions.jsonl"
            rows = list(parse_jsonl(path.read_bytes()))
            row = object_value(rows[0])
            row["status"] = status
            del row["output"]
            row["failure"] = {"code": "timeout", "message": "Synthetic failure."}
            path.write_text("\n".join(json.dumps(value) for value in rows) + "\n", encoding="utf-8")
            ready = read_document(directory / "inference-complete.json", InferenceComplete)
            ready["predictions_sha256"] = sha256(path.read_bytes()).hexdigest()
            (directory / "inference-complete.json").write_text(json.dumps(ready), encoding="utf-8")
            with self.assertRaises(ValueError):
                score_run(directory, self.dataset)

    def test_excessive_json_nesting_and_overflow_are_validation_errors(self):
        for text in ("[" * 10000 + "]" * 10000, '{"value":1e400}'):
            with self.subTest(text=text[:20]), self.assertRaises(ValueError):
                parse_json(text)

    def test_dataset_hash_coverage_and_answer_leakage_rejected(self):
        inputs = self.dataset / "inputs/development.jsonl"
        original = inputs.read_bytes()
        for raw in (
            original + b" ",
            b'{"case_id":"D1","transcript":"x","expected_label":"no_callback"}\n',
        ):
            inputs.write_bytes(raw)
            with self.assertRaises(ValueError):
                load_split(self.dataset, "development")
        inputs.write_bytes(original)
        dataset = load_split(self.dataset, "development")
        (self.dataset / "answers/development.jsonl").write_bytes(b"modified")
        with self.assertRaises(ValueError):
            load_answers(dataset)

    def test_held_out_requires_opt_in_and_freeze_before_dataset_or_model_access(self):
        with patch(
            "voice_callback.evaluate.load_split", side_effect=AssertionError("Dataset opened")
        ):
            for allow, path in ((False, None), (True, None), (False, self.folder / "missing.json")):
                with self.assertRaises(ValueError):
                    evaluate(
                        self.dataset,
                        "evaluation",
                        MODEL,
                        FakeOllama(),
                        allow_held_out=allow,
                        frozen_path=path,
                    )

    def test_clean_baseline_freezes_and_synthetic_held_out_rejects_changed_system(self):
        with patch(
            "voice_callback.evaluation_config.subprocess.check_output", side_effect=self.clean_git
        ):
            directory = self.run_evaluation()
            frozen = freeze_run(directory, self.dataset)
            self.assertEqual(freeze_run(directory, self.dataset), frozen)
            result = evaluate(
                self.dataset,
                "evaluation",
                MODEL,
                FakeOllama(),
                output_root=self.output,
                policy_path=ROOT / "docs/CALLBACK_POLICY.md",
                allow_held_out=True,
                frozen_path=frozen,
            )
            self.assertEqual(
                read_document(result / "report.json", EvaluationReport)["split"], "evaluation"
            )
            changed = FakeOllama()
            changed.digest = "changed"
            with self.assertRaises(ValueError):
                evaluate(
                    self.dataset,
                    "evaluation",
                    MODEL,
                    changed,
                    output_root=self.output,
                    policy_path=ROOT / "docs/CALLBACK_POLICY.md",
                    allow_held_out=True,
                    frozen_path=frozen,
                )
            self.assertEqual(changed.requests, [])

    def test_dirty_or_different_revision_cannot_freeze_or_run_held_out(self):
        with patch(
            "voice_callback.evaluation_config.subprocess.check_output", side_effect=self.clean_git
        ):
            directory = self.run_evaluation()
            frozen = freeze_run(directory, self.dataset)
        with patch(
            "voice_callback.evaluation_config.subprocess.check_output", return_value="dirty"
        ):
            with self.assertRaises(ValueError):
                freeze_run(directory, self.dataset, self.folder / "another.json")
            with self.assertRaises(ValueError):
                evaluate(
                    self.dataset,
                    "evaluation",
                    MODEL,
                    FakeOllama(),
                    allow_held_out=True,
                    frozen_path=frozen,
                )

    def test_shared_json_parser_rejects_duplicates_nonfinite_numbers_and_blank_records(self):
        for value in ('{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                parse_json(value)
        with self.assertRaises(ValueError):
            parse_jsonl(b'{"x":1}\n\n')

    def test_cli_evaluate_score_and_freeze_exit_codes_and_offline_boundaries(self):
        args = [
            "evaluate",
            "--dataset",
            str(self.dataset),
            "--split",
            "development",
            "--model",
            MODEL.id,
            "--output-dir",
            str(self.output),
        ]
        with (
            patch("voice_callback.cli.OllamaClient", return_value=FakeOllama()),
            redirect_stdout(StringIO()) as stdout,
        ):
            self.assertEqual(main(args), 0)
        report = json.loads(stdout.getvalue())
        directory = Path(report["report_path"]).parent
        with (
            patch(
                "voice_callback.cli.OllamaClient", side_effect=AssertionError("Inference called")
            ),
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(
                main(["score", "--run-dir", str(directory), "--dataset", str(self.dataset)]), 0
            )
        with (
            patch("voice_callback.evaluation_config.subprocess.check_output", return_value="dirty"),
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(
                main(
                    [
                        "freeze-evaluation",
                        "--run-dir",
                        str(directory),
                        "--dataset",
                        str(self.dataset),
                    ]
                ),
                2,
            )
        with (
            patch(
                "voice_callback.cli.OllamaClient",
                return_value=FakeOllama([FailureCode.TIMEOUT, Outcome.NO_CALLBACK]),
            ),
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(main(args), 1)
        with redirect_stdout(StringIO()):
            self.assertEqual(main(["score", "--run-dir", str(self.folder / "missing")]), 1)
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            main(["evaluate", "--split", "development"])
