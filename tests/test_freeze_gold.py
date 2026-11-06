"""Exercise approval gates, immutable releases, and classifier-input isolation."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts/freeze_gold.py"


class GoldFreezeChecks(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(dir=scratch)
        self.base = Path(self.workspace.name)
        if not self.base.resolve().is_relative_to(scratch.resolve()):
            raise RuntimeError("Test workspace escaped scratch root")
        self.addCleanup(self.workspace.cleanup)
        self.source = self.base / "candidates.jsonl"
        self.review = self.base / "approval.json"
        self.policy = self.base / "policy.md"
        self.output = self.base / "gold"
        self.source.write_bytes((ROOT / "data/candidates/v0.1/cases.jsonl").read_bytes())
        self.review.write_bytes((ROOT / "data/reviews/v1.0.json").read_bytes())
        self.policy.write_bytes((ROOT / "docs/CALLBACK_POLICY.md").read_bytes())

    def run_export(self, *extra):
        return subprocess.run(
            [sys.executable, str(EXPORTER), "--source", str(self.source),
             "--review", str(self.review), "--policy", str(self.policy),
             "--output", str(self.output), *extra],
            capture_output=True, text=True, encoding="utf-8",
        )

    def change_review(self, **updates):
        value = json.loads(self.review.read_text(encoding="utf-8"))
        value.update(updates)
        self.review.write_text(json.dumps(value), encoding="utf-8")

    def test_freezes_all_approved_labels_and_separates_inputs(self):
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.output / "manifest.json").read_text())
        self.assertEqual(manifest["case_count"], 40)
        self.assertEqual(manifest["family_count"], 20)
        for split in ("development", "evaluation"):
            inputs = [json.loads(line) for line in (self.output / f"inputs/{split}.jsonl").read_text().splitlines()]
            answers = [json.loads(line) for line in (self.output / f"answers/{split}.jsonl").read_text().splitlines()]
            self.assertEqual(len(inputs), 20)
            self.assertEqual([r["case_id"] for r in inputs], [r["case_id"] for r in answers])
            for row in inputs:
                self.assertEqual(set(row), {"case_id", "transcript"})
        for name, metadata in manifest["files"].items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(),
                             metadata["sha256"])

    def test_reviewed_without_approval_does_not_export(self):
        self.change_review(decision="reviewed")
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Explicit human approval", result.stderr)
        self.assertFalse(self.output.exists())

    def test_partial_approval_does_not_export_the_whole_set(self):
        review = json.loads(self.review.read_text())
        self.change_review(approved_case_ids=review["approved_case_ids"][:-1])
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("every source case", result.stderr)
        self.assertFalse(self.output.exists())

    def test_changed_candidate_source_requires_new_approval(self):
        self.source.write_bytes(self.source.read_bytes() + b"\n")
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source hash", result.stderr)
        self.assertFalse(self.output.exists())

    def test_repeat_does_not_rewrite_existing_release(self):
        self.assertEqual(self.run_export().returncode, 0)
        before = {p.relative_to(self.output): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(self.run_export().returncode, 0)
        after = {p.relative_to(self.output): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_differing_release_is_preserved(self):
        self.assertEqual(self.run_export().returncode, 0)
        path = self.output / "inputs/evaluation.jsonl"
        path.write_text("existing changed artifact", encoding="utf-8")
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not overwritten", result.stderr)
        self.assertEqual(path.read_text(), "existing changed artifact")

    def test_check_detects_input_label_leakage(self):
        self.assertEqual(self.run_export().returncode, 0)
        path = self.output / "inputs/evaluation.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]["expected_label"] = "callback_required"
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        result = self.run_export("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Frozen content differs", result.stderr)

    def test_wrong_policy_is_rejected_before_export(self):
        self.policy.write_text("An unrelated policy document", encoding="utf-8")
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("policy hash", result.stderr)
        self.assertFalse(self.output.exists())

    def test_unapproved_policy_version_is_rejected(self):
        self.change_review(policy_version="2.0")
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("policy version", result.stderr)
        self.assertFalse(self.output.exists())

    def test_actual_gold_release_verifies(self):
        result = subprocess.run(
            [sys.executable, str(EXPORTER), "--check"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
