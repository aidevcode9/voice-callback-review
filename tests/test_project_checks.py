"""Prove missing gates, snapshot drift, and failing subprocesses stop verification."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_project import ROOT, documentation_errors, run, workflow_errors
from scripts.codex_preflight import export_tree


class ProjectGateBehavior(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name).resolve()

    def test_subprocess_failure_is_a_blocking_failure(self):
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            run([sys.executable, "-c", "raise SystemExit(7)"], cwd=self.folder)
        self.assertEqual(caught.exception.returncode, 7)

    def test_missing_links_and_duplicate_feature_lifecycle_are_rejected(self):
        (self.folder / "README.md").write_text("[missing](missing.md)")
        for state in ("active", "completed"):
            feature = self.folder / "features" / state / "F-001-example"
            feature.mkdir(parents=True)
            (feature / "FEATURE.md").write_text("# Feature")
        _, errors = documentation_errors(self.folder)
        self.assertTrue(any("missing target" in error for error in errors))
        self.assertTrue(any("Duplicate feature ID" in error for error in errors))

    def test_mutable_action_revision_is_rejected(self):
        workflow = self.folder / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            (ROOT / ".github/workflows/ci.yml")
            .read_text()
            .replace(
                "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803", "actions/checkout@main"
            )
        )
        self.assertTrue(any("immutable commit" in error for error in workflow_errors(self.folder)))

    def test_ci_cannot_omit_the_shared_type_and_lint_suite(self):
        workflow = self.folder / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            (ROOT / ".github/workflows/ci.yml")
            .read_text()
            .replace("python scripts/check_project.py --suite quality", "echo skipped quality")
        )
        self.assertTrue(
            any("shared quality suite" in error for error in workflow_errors(self.folder))
        )

    def git(self, *args: str):
        return subprocess.run(["git", *args], cwd=self.folder, check=True, capture_output=True)

    def prepare_git_fixture(self):
        self.git("init", "--initial-branch=main")
        (self.folder / "sample.py").write_text("COMMITTED = True\n", newline="\n")
        self.git("add", "sample.py")
        self.git(
            "-c",
            "user.name=Quality fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Fixture",
        )
        (self.folder / "sample.py").write_text("STAGED = True\n", newline="\n")
        self.git("add", "sample.py")
        (self.folder / "sample.py").write_text("UNSTAGED = True\n", newline="\n")
        (self.folder / "untracked.py").write_text("UNTRACKED = True\n")

    def test_pre_commit_reads_staged_content_without_working_tree_substitution(self):
        self.prepare_git_fixture()
        snapshot = self.folder / "staged-export"
        snapshot.mkdir()
        export_tree(self.folder, snapshot, "pre-commit")
        self.assertEqual((snapshot / "sample.py").read_text(), "STAGED = True\n")
        self.assertFalse((snapshot / "untracked.py").exists())
        self.assertEqual((self.folder / "sample.py").read_text(), "UNSTAGED = True\n")

    def test_review_reads_head_even_when_index_and_working_tree_differ(self):
        self.prepare_git_fixture()
        snapshot = self.folder / "head-export"
        snapshot.mkdir()
        export_tree(self.folder, snapshot, "review")
        self.assertEqual((snapshot / "sample.py").read_text(), "COMMITTED = True\n")
        self.assertFalse((snapshot / "untracked.py").exists())
