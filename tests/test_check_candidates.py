"""Exercise the data validator's observable CLI behavior."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_candidates.py"
CASE = {
    "case_id": "VC-999", "family_id": "FAM-999", "suggested_split": "development",
    "source": "synthetic", "transcript": "Caller: My issue is still unresolved.",
    "proposed_label": "callback_required", "rule_ids": ["UR-001"],
    "rationale": "The issue remains unresolved.", "evidence": ["My issue is still unresolved."],
    "review_status": "pending", "reviewed_label": None, "reviewer": None,
}


class CandidateChecks(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(dir=scratch)
        self.base = Path(self.workspace.name)
        if not self.base.resolve().is_relative_to(scratch.resolve()):
            raise RuntimeError("Test workspace escaped scratch root")
        self.addCleanup(self.workspace.cleanup)
        self.path = self.base / "cases.jsonl"

    def run_records(self, records):
        self.path.write_text(
            "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
        )
        return self.run_path(self.path)

    def run_path(self, path):
        return subprocess.run(
            [sys.executable, str(CHECKER), str(path)],
            capture_output=True, text=True, encoding="utf-8",
        )

    def test_valid_pending_case_passes_and_is_not_rewritten(self):
        result = self.run_records([CASE])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["review_statuses"], {"pending": 1})
        before = self.path.read_bytes()
        self.assertEqual(self.run_path(self.path).returncode, 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_unsupported_evidence_fails(self):
        row = copy.deepcopy(CASE)
        row["evidence"] = ["A promise that does not appear in the call."]
        result = self.run_records([row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence quote", result.stderr)

    def test_duplicate_ids_fail(self):
        result = self.run_records([CASE, CASE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate case_id", result.stderr)

    def test_family_cannot_cross_splits(self):
        row = copy.deepcopy(CASE)
        row.update(case_id="VC-998", suggested_split="evaluation",
                   transcript="Caller: My issue is still unresolved. No answer yet.")
        result = self.run_records([CASE, row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("family occurs in more than one split", result.stderr)

    def test_identical_transcript_cannot_cross_splits_under_different_family(self):
        row = copy.deepcopy(CASE)
        row.update(case_id="VC-998", family_id="FAM-998", suggested_split="evaluation")
        result = self.run_records([CASE, row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate transcript", result.stderr)

    def test_approved_label_requires_a_reviewer(self):
        row = copy.deepcopy(CASE)
        row.update(review_status="approved", reviewed_label="callback_required")
        result = self.run_records([row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reviewer is required", result.stderr)

    def test_pending_case_cannot_have_a_reviewed_label(self):
        row = copy.deepcopy(CASE)
        row["reviewed_label"] = "callback_required"
        result = self.run_records([row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pending records", result.stderr)

    def test_nonobject_record_fails_without_traceback(self):
        result = self.run_records([["not", "a", "record"]])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("record must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_transcript_fails_without_traceback(self):
        row = copy.deepcopy(CASE)
        del row["transcript"]
        result = self.run_records([row])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transcript must be", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_actual_starter_set_is_pending_and_has_both_splits(self):
        result = self.run_path(ROOT / "data/candidates/v0.1/cases.jsonl")
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["cases"], 40)
        self.assertEqual(summary["families"], 20)
        self.assertEqual(summary["splits"], {"development": 20, "evaluation": 20})
        self.assertEqual(summary["review_statuses"], {"pending": 40})
        for counts in summary["labels_by_split"].values():
            self.assertEqual(set(counts), {"callback_required", "no_callback", "needs_review"})

    def test_actual_review_packet_matches_the_data(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/render_candidate_review.py"),
             str(ROOT / "data/candidates/v0.1/cases.jsonl"), "--check"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_renderer_cannot_replace_its_candidate_input(self):
        self.run_records([CASE])
        before = self.path.read_bytes()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/render_candidate_review.py"),
             str(self.path), "--output", str(self.path)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must differ", result.stderr)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
