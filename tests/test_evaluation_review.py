"""Review preserved synthetic evaluations without model or held-out data access."""

import json
import unittest
from dataclasses import replace
from hashlib import sha256
from unittest.mock import patch

import test_evaluate as fixtures

from voice_callback.datasets import load_split
from voice_callback.domain import FailureCode, Outcome
from voice_callback.evaluate import score_run
from voice_callback.evaluation_review import (
    assert_baseline_compatible,
    compare_reviews,
    load_review,
    render_review,
    summary_text,
)


class EvaluationReviewBehavior(unittest.TestCase):
    def setUp(self):
        # Reuse setup/data builders without importing or subclassing its TestCase.
        self.fixture = fixtures.EvaluationArtifacts()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.identity = {
            "source_sha256": "a" * 64,
            "git_revision": "b" * 40,
            "working_tree_clean": True,
        }

    def make_review(self, outcomes=None):
        with (
            patch("voice_callback.evaluation_config.source_identity", return_value=self.identity),
            patch("voice_callback.evaluate.source_identity", return_value=self.identity),
        ):
            directory = self.fixture.run_evaluation(fixtures.FakeOllama(outcomes))
        return load_review(directory, self.fixture.dataset)

    def test_reads_all_cases_metrics_and_original_source_without_rerunning_it(self):
        review = self.make_review()
        self.assertEqual(review.report.score.correct_outputs, 2)
        self.assertEqual(len(review.cases), 2)
        self.assertEqual(review.system.code.source_sha256, "a" * 64)
        self.assertIn("Historical source not rerun", review.verification)
        with patch("voice_callback.evaluate.source_identity", return_value={"source_sha256": "x"}):
            with self.assertRaisesRegex(ValueError, "identity differs"):
                score_run(review.directory, self.fixture.dataset)
        text = summary_text(review)
        self.assertIn("Callback recall: 1/1 (100.0%)", text)
        self.assertIn("not established", text)

    def test_rejects_held_out_declaration_before_dataset_or_answers_are_opened(self):
        review = self.make_review()
        path = review.directory / "evaluation.json"
        declaration = json.loads(path.read_text())
        declaration["split"] = "evaluation"
        path.write_text(json.dumps(declaration))
        with (
            patch("voice_callback.evaluation_review.load_split") as dataset,
            patch("voice_callback.evaluation_review.load_answers") as answers,
        ):
            with self.assertRaisesRegex(ValueError, "held-out"):
                load_review(review.directory, self.fixture.dataset)
            dataset.assert_not_called()
            answers.assert_not_called()

    def test_rejects_corrupted_predictions_before_answers_are_opened(self):
        review = self.make_review()
        with (review.directory / "predictions.jsonl").open("ab") as stream:
            stream.write(b" ")
        with patch("voice_callback.evaluation_review.load_answers") as answers:
            with self.assertRaisesRegex(ValueError, "artifact hashes differ"):
                load_review(review.directory, self.fixture.dataset)
            answers.assert_not_called()

    def test_incomplete_marker_prevents_report_review(self):
        review = self.make_review()
        (review.directory / "aborted.json").write_text('{"status":"incomplete"}')
        with patch("voice_callback.evaluation_review.load_answers") as answers:
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                load_review(review.directory, self.fixture.dataset)
            answers.assert_not_called()

    def test_missing_completion_marker_prevents_answer_read(self):
        review = self.make_review()
        (review.directory / "inference-complete.json").unlink()
        with patch("voice_callback.evaluation_review.load_answers") as answers:
            with self.assertRaises(FileNotFoundError):
                load_review(review.directory, self.fixture.dataset)
            answers.assert_not_called()

    def test_saved_counts_cannot_disagree_with_saved_predictions(self):
        review = self.make_review()
        report_path = review.directory / "report.json"
        report = json.loads(report_path.read_text())
        report["score"]["correct_outputs"] = 0
        report_path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "Saved report counts differ"):
            load_review(review.directory, self.fixture.dataset)

    def test_case_configuration_mismatch_is_rejected_before_answer_read(self):
        review = self.make_review()
        prediction_path = review.directory / "predictions.jsonl"
        predictions = [json.loads(row) for row in prediction_path.read_text().splitlines()]
        run_path = review.directory / "runs" / f"{predictions[0]['run_id']}.json"
        run = json.loads(run_path.read_text())
        run["run"]["provenance"]["model"]["model_id"] = "another-local-model"
        run_path.write_text(json.dumps(run))
        predictions[0]["run_sha256"] = sha256(run_path.read_bytes()).hexdigest()
        prediction_path.write_text("\n".join(json.dumps(row) for row in predictions) + "\n")
        digest = sha256(prediction_path.read_bytes()).hexdigest()
        for name in ("inference-complete.json", "report.json"):
            path = review.directory / name
            document = json.loads(path.read_text())
            document["predictions_sha256"] = digest
            path.write_text(json.dumps(document))
        with patch("voice_callback.evaluation_review.load_answers") as answers:
            with self.assertRaisesRegex(ValueError, "case provenance differs"):
                load_review(review.directory, self.fixture.dataset)
            answers.assert_not_called()

    def test_comparison_exposes_regression_unsafe_miss_and_undefined_delta(self):
        baseline = self.make_review()
        current = self.make_review([Outcome.NO_CALLBACK, Outcome.NO_CALLBACK])
        comparison = compare_reviews(current, baseline)
        self.assertEqual(comparison.regressions, ("D1",))
        self.assertEqual(comparison.new_unsafe_misses, ("D1",))
        self.assertEqual(comparison.fixes, ())
        precision = next(row for row in comparison.metrics if row.name == "callback_precision")
        self.assertIsNone(precision.current.value)
        self.assertIsNone(precision.percentage_points)
        reverse = compare_reviews(baseline, current)
        self.assertEqual(reverse.fixes, ("D1",))
        self.assertEqual(reverse.removed_unsafe_misses, ("D1",))

    def test_processing_failure_changes_are_visible_separately_from_labels(self):
        baseline = self.make_review()
        current = self.make_review([FailureCode.INVALID_OUTPUT, Outcome.NO_CALLBACK])
        comparison = compare_reviews(current, baseline)
        self.assertEqual(comparison.regressions, ("D1",))
        self.assertEqual(comparison.new_unsafe_misses, ())
        self.assertIn("processing failures: 1", summary_text(current, comparison))
        html = render_review(current, baseline).read_text(encoding="utf-8")
        self.assertIn("Processing failure", html)
        self.assertIn("invalid_output", html)

    def test_preflight_rejects_changed_dataset_or_case_hash(self):
        baseline = self.make_review()
        dataset = load_split(self.fixture.dataset, "development")
        assert_baseline_compatible(baseline, dataset)
        for changed in (
            replace(dataset, version="other"),
            replace(dataset, inputs_sha256="0" * 64),
            replace(dataset, answers_sha256="0" * 64),
            replace(dataset, name="evaluation"),
            replace(dataset, transcripts=(dataset.transcripts[0],)),
        ):
            with (
                self.subTest(dataset=changed),
                self.assertRaisesRegex(ValueError, "same development"),
            ):
                assert_baseline_compatible(baseline, changed)

    def test_model_prompt_and_code_differences_remain_comparable(self):
        baseline = self.make_review()
        current = self.make_review()
        changed_system = current.system.model_copy(update={"prompt_version": "new-prompt"})
        current = replace(current, system=changed_system)
        comparison = compare_reviews(current, baseline)
        self.assertEqual(comparison.configuration_changes, ("prompt_version",))
        self.assertEqual(comparison.regressions, ())

    def test_incompatible_definitions_cannot_be_compared(self):
        baseline = self.make_review()
        current = self.make_review()
        definitions = current.report.definitions.model_copy(update={"undefined": "Changed rule"})
        current = replace(
            current, report=current.report.model_copy(update={"definitions": definitions})
        )
        with self.assertRaisesRegex(ValueError, "definitions differ"):
            compare_reviews(current, baseline)

    def test_report_is_idempotent_preserves_originals_and_escapes_transcript(self):
        source = self.fixture.dataset / "inputs/development.jsonl"
        rows = [json.loads(row) for row in source.read_text(encoding="utf-8").split("\n") if row]
        rows[0]["transcript"] += " <script>alert('fictional')</script>"
        content = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
        source.write_bytes(content)
        manifest_path = self.fixture.dataset / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"]["inputs/development.jsonl"]["sha256"] = sha256(content).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        baseline = self.make_review()
        current = self.make_review()
        originals = {
            path: path.read_bytes() for path in current.directory.rglob("*") if path.is_file()
        }
        baseline_files = {
            path: path.read_bytes() for path in baseline.directory.rglob("*") if path.is_file()
        }
        path = render_review(current, baseline)
        before = path.stat().st_mtime_ns
        self.assertEqual(render_review(current, baseline), path)
        self.assertEqual(path.stat().st_mtime_ns, before)
        html = path.read_text(encoding="utf-8")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("Confusion matrix", html)
        self.assertIn("Approved reference", html)
        self.assertIn("ANSWER_ONLY_DEV", html)
        self.assertIn("What changed?", html)
        self.assertEqual(originals, {path: path.read_bytes() for path in originals})
        self.assertEqual(baseline_files, {path: path.read_bytes() for path in baseline_files})
        path.write_text("Existing unrelated derived report", encoding="utf-8")
        revised = render_review(current, baseline)
        self.assertNotEqual(revised, path)
        self.assertTrue(revised.name.startswith(f"review-baseline-{baseline.report_sha256}-"))
        self.assertEqual(revised.read_bytes(), html.encode())
        self.assertEqual(render_review(current, baseline), revised)
        self.assertEqual(path.read_text(), "Existing unrelated derived report")

    def test_changed_plain_projection_uses_a_content_suffix_without_overwriting(self):
        current = self.make_review()
        first = render_review(current)
        original_html = first.read_bytes()
        first.write_text("Earlier renderer output", encoding="utf-8")
        revised = render_review(current)
        self.assertEqual(revised.name, f"review-{sha256(original_html).hexdigest()[:16]}.html")
        self.assertEqual(first.read_text(), "Earlier renderer output")
        self.assertEqual(revised.read_bytes(), original_html)
        self.assertEqual(render_review(current), revised)
        revised.write_text("Conflicting content at exact hash path", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "content-addressed review differs"):
            render_review(current)


if __name__ == "__main__":
    unittest.main()
