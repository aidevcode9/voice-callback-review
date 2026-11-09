"""Run the canonical command against committed synthetic source and controlled HTTP."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from test_evaluate import FakeOllama

from voice_callback.domain import Outcome
from voice_callback.evaluation_config import digest_json

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def synthetic_runtime():
    adapter = FakeOllama(
        [
            Outcome.CALLBACK_REQUIRED,
            Outcome.CALLBACK_REQUIRED,
            Outcome.CALLBACK_REQUIRED,
            Outcome.NO_CALLBACK,
        ]
    )
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.command, self.path))
            if self.path == "/api/version":
                payload = {"version": adapter.version()}
            elif self.path == "/api/tags":
                payload = {
                    "models": [
                        {"name": model.name, "digest": model.digest}
                        for model in adapter.installed_models()
                    ]
                }
            else:
                self.send_error(404)
                return
            self.respond(payload)

        def do_POST(self):
            requests.append((self.command, self.path))
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if self.path == "/api/show":
                payload = adapter.show(body["model"])
            elif self.path == "/api/chat":
                payload = adapter.chat(body)
            else:
                self.send_error(404)
                return
            self.respond(payload)

        def respond(self, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", adapter, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class CanonicalEvaluationIntegration(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        package = self.root / "src/voice_callback"
        shutil.copytree(
            ROOT / "src/voice_callback",
            package,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        (self.root / "src/langfuse.py").write_text(
            "from pathlib import Path\n"
            "Path('runtime').mkdir(exist_ok=True)\n"
            "Path('runtime/telemetry-imported').write_text('unexpected SDK import')\n"
            "raise RuntimeError('Synthetic telemetry must remain disabled')\n",
            encoding="utf-8",
        )
        for relative in ("config/models.json", "docs/CALLBACK_POLICY.md"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        (self.root / ".gitignore").write_text(
            ".test-work/\nreports/\nruntime/\n.env\n__pycache__/\n*.pyc\n", encoding="utf-8"
        )
        self.create_dataset()
        self.git("init", "--quiet")
        self.git("config", "core.autocrlf", "false")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Committed synthetic evaluation implementation",
        )
        self.revision = self.git("rev-parse", "HEAD")
        self.source_digest = digest_json(
            {
                path.relative_to(package).as_posix(): sha256(path.read_bytes()).hexdigest()
                for path in sorted([*package.glob("*.py"), *package.glob("prompts/*.txt")])
            }
        )
        self.environment = os.environ.copy()
        self.environment["PYTHONPATH"] = str(ROOT / "src")
        self.environment.pop("PYTHONHOME", None)
        self.environment["VCR_LANGFUSE_ENABLED"] = "1"
        self.environment["LANGFUSE_TRACING_ENABLED"] = "true"
        self.environment["LANGFUSE_PUBLIC_KEY"] = "fixture-public-value"
        self.environment["LANGFUSE_SECRET_KEY"] = "fixture-private-value"
        self.environment["LANGFUSE_BASE_URL"] = "http://127.0.0.1:1"
        (self.root / ".env").write_text(
            "LANGFUSE_SECRET_KEY=fixture-private-value\n", encoding="utf-8"
        )

    def git(self, *arguments):
        return subprocess.check_output(
            ["git", *arguments], cwd=self.root, stderr=subprocess.PIPE, text=True
        ).strip()

    def create_dataset(self):
        dataset = self.root / "data/gold/synthetic"
        inputs = [
            {"case_id": "D1", "transcript": "Caller: Please call me back."},
            {
                "case_id": "D2",
                "transcript": (
                    "Caller: Earlier I said, 'Please call me back.' I withdraw that request; "
                    "everything is resolved. No callback is needed."
                ),
            },
        ]
        answers = [
            {
                "case_id": "D1",
                "expected_label": "callback_required",
                "rationale": "ANSWER_ONLY_INTEGRATION: outstanding caller request.",
                "rule_ids": ["CB-002"],
                "evidence": ["Please call me back"],
            },
            {
                "case_id": "D2",
                "expected_label": "no_callback",
                "rationale": "ANSWER_ONLY_INTEGRATION: withdrawal and resolution.",
                "rule_ids": ["NC-001"],
                "evidence": ["No callback is needed"],
            },
        ]
        files = {}
        for part, rows in (("inputs", inputs), ("answers", answers)):
            relative = f"{part}/development.jsonl"
            target = dataset / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = ("\n".join(json.dumps(row) for row in rows) + "\n").encode("utf-8")
            target.write_bytes(raw)
            files[relative] = {"sha256": sha256(raw).hexdigest()}
        (dataset / "manifest.json").write_text(
            json.dumps(
                {
                    "dataset_version": "synthetic-integration-v1",
                    "status": "frozen",
                    "splits": {"development": ["D1", "D2"]},
                    "files": files,
                }
            ),
            encoding="utf-8",
        )

    def command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "voice_callback.cli", *arguments],
            cwd=self.root,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def completed_run(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("fixture-private-value", result.stdout + result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual(document["status"], "completed")
        directory = Path(document["report_path"]).parent
        self.assertEqual(directory.parent, self.root / "reports/text")
        self.assertTrue((directory / "report.json").is_file())
        review_path = Path(document["review_path"])
        self.assertEqual(review_path.parent, directory)
        self.assertTrue(review_path.is_file())
        configuration = (directory / "configuration.json").read_text(encoding="utf-8")
        self.assertNotIn("fixture-private-value", configuration)
        self.assertNotIn("fixture-private-value", (directory / "report.json").read_text())
        system = json.loads(configuration)
        self.assertEqual(
            system["code"],
            {
                "git_revision": self.revision,
                "working_tree_clean": True,
                "source_sha256": self.source_digest,
            },
        )
        self.assertIn("1/2 saved: D1", result.stderr)
        self.assertIn("2/2 saved: D2", result.stderr)
        self.assertIn("Evaluation completed.", result.stderr)
        checkout = self.root / ".test-work/evaluation-worktrees" / self.revision
        self.assertIn(str(checkout), result.stderr)
        self.assertFalse((checkout / "runtime/telemetry-imported").exists())
        self.assertEqual(self.git("status", "--porcelain"), "")
        return directory, document

    def test_real_command_runs_compares_reviews_and_rejects_dirty_source_without_inference(self):
        with synthetic_runtime() as (url, adapter, requests):
            arguments = [
                "evaluate",
                "--model",
                "qwen35-4b",
                "--dataset",
                "data/gold/synthetic",
                "--no-trace",
                "--json",
                "--url",
                url,
            ]
            first, document = self.completed_run(self.command(*arguments))
            report = document["report"]
            self.assertEqual((report["score"]["total"], report["score"]["correct_outputs"]), (2, 1))
            self.assertTrue((first / "review.html").is_file())
            self.assertEqual(len(adapter.requests), 2)
            original_report = (first / "report.json").read_bytes()

            second, document = self.completed_run(
                self.command(*arguments, "--baseline", str(first))
            )
            report = document["report"]
            self.assertNotEqual(first, second)
            self.assertEqual(report["score"]["correct_outputs"], 2)
            self.assertEqual(document["comparison"]["fixes"], ["D2"])
            self.assertEqual(document["comparison"]["regressions"], [])
            comparison = Path(document["review_path"]).read_text(encoding="utf-8")
            self.assertIn(first.name, comparison)
            self.assertIn("D2", comparison)
            self.assertIn("fix", comparison.lower())
            self.assertEqual(len(adapter.requests), 4)
            self.assertNotIn("ANSWER_ONLY_INTEGRATION", json.dumps(adapter.requests))
            self.assertNotIn("fixture-private-value", json.dumps(adapter.requests))
            self.assertEqual((first / "report.json").read_bytes(), original_report)

            request_count = len(requests)
            review = self.command(
                "evaluations",
                "--run-dir",
                str(second),
                "--baseline",
                str(first),
                "--dataset",
                "data/gold/synthetic",
            )
            self.assertEqual(review.returncode, 0, review.stdout + review.stderr)
            self.assertIn("1 fixes; 0 regressions", review.stdout)
            self.assertEqual(len(requests), request_count)

            source = self.root / "src/voice_callback/evaluation_worker.py"
            source.write_text(source.read_text(encoding="utf-8") + "\n# dirty fixture\n")
            refused = self.command(*arguments)
            self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
            self.assertIn("Commit or set aside", json.loads(refused.stdout)["message"])
            self.assertEqual(len(requests), request_count)
            self.assertEqual(len(list((self.root / "reports/text").iterdir())), 2)

    def test_clean_crlf_workspace_can_rescore_freeze_and_run_explicit_synthetic_held_out(self):
        # Match the project's LF Git attributes while keeping a Git-clean CRLF caller.
        for relative in self.git("ls-files").splitlines():
            path = self.root / relative
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        (self.root / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
        caller = self.root / "src/voice_callback/cli.py"
        caller.write_bytes(caller.read_bytes().replace(b"\n", b"\r\n"))
        dataset = self.root / "data/gold/synthetic"
        manifest = json.loads((dataset / "manifest.json").read_bytes())
        manifest["splits"]["evaluation"] = ["H1", "H2"]
        for part in ("inputs", "answers"):
            rows = [
                json.loads(row)
                for row in (dataset / part / "development.jsonl").read_text().splitlines()
            ]
            for row in rows:
                row["case_id"] = row["case_id"].replace("D", "H", 1)
            raw = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
            relative = f"{part}/evaluation.jsonl"
            (dataset / relative).write_bytes(raw)
            manifest["files"][relative] = {"sha256": sha256(raw).hexdigest()}
        (dataset / "manifest.json").write_bytes(json.dumps(manifest).encode())
        self.git("add", ".")
        self.git("add", "--renormalize", ".")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Normalize synthetic committed source",
        )
        self.revision = self.git("rev-parse", "HEAD")
        package = self.root / "src/voice_callback"
        self.source_digest = digest_json(
            {
                path.relative_to(package).as_posix(): sha256(
                    subprocess.check_output(
                        [
                            "git",
                            "show",
                            f"HEAD:src/voice_callback/{path.relative_to(package).as_posix()}",
                        ],
                        cwd=self.root,
                    )
                ).hexdigest()
                for path in sorted([*package.glob("*.py"), *package.glob("prompts/*.txt")])
            }
        )
        self.environment["PYTHONPATH"] = str(self.root / "src")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertIn(b"\r\n", caller.read_bytes())
        with synthetic_runtime() as (url, adapter, requests):
            directory, _ = self.completed_run(
                self.command(
                    "evaluate",
                    "--model",
                    "qwen35-4b",
                    "--dataset",
                    "data/gold/synthetic",
                    "--no-trace",
                    "--json",
                    "--url",
                    url,
                )
            )
            original = (directory / "report.json").read_bytes()
            request_count = len(requests)
            for operation in ("score", "freeze-evaluation"):
                result = self.command(
                    operation, "--run-dir", str(directory), "--dataset", "data/gold/synthetic"
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                len(requests), request_count, "Artifact operations must make no HTTP calls."
            )
            self.assertEqual((directory / "report.json").read_bytes(), original)
            frozen = directory / "frozen-configuration.json"
            self.assertTrue(frozen.exists())
            self.environment["VCR_LANGFUSE_ENABLED"] = "0"
            held_out = [
                "evaluate",
                "--split",
                "evaluation",
                "--model",
                "qwen35-4b",
                "--dataset",
                "data/gold/synthetic",
                "--url",
                url,
                "--frozen-config",
                str(frozen),
                "--json",
            ]
            refused = self.command(*held_out)
            self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
            self.assertEqual(len(requests), request_count)
            completed = self.command(*held_out, "--allow-held-out")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["report"]["split"], "evaluation")
            self.assertEqual(len(adapter.requests), 4)
            self.assertNotIn("ANSWER_ONLY_INTEGRATION", json.dumps(adapter.requests))
            self.assertEqual(self.git("status", "--porcelain"), "")
            source = self.root / "src/voice_callback/evaluation_worker.py"
            source.write_bytes(
                source.read_bytes() + b"\n# Changed source must not rescore an older run.\n"
            )
            self.git("add", ".")
            self.git(
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "Change synthetic source",
            )
            request_count = len(requests)
            for operation in ("score", "freeze-evaluation"):
                result = self.command(
                    operation, "--run-dir", str(directory), "--dataset", "data/gold/synthetic"
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("identity differs", result.stdout)
            self.assertEqual(len(requests), request_count)


if __name__ == "__main__":
    unittest.main()
