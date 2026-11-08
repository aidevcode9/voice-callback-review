"""Prove checkout selection, preflight ordering and the CLI adapter without inference."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from voice_callback.cli import main
from voice_callback.evaluation_workflow import DevelopmentRequest, prepare_checkout, run_development

ROOT = Path(__file__).resolve().parents[1]


class EvaluationWorkflowTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for path, content in {
            ".gitignore": ".test-work/\n.env\n",
            "src/voice_callback/__init__.py": "",
            "src/voice_callback/evaluation_worker.py": "import json, os; print(json.dumps({'worker': __file__, 'tracing': os.environ.get('VCR_LANGFUSE_ENABLED')}))\n",
            "config/models.json": "{}",
            "docs/CALLBACK_POLICY.md": "fixture",
            "data/gold/fixture/manifest.json": "{}",
        }.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Synthetic fixture",
        )
        self.request = DevelopmentRequest(
            repository=self.root,
            model_id="fixture",
            dataset=self.root / "data/gold/fixture",
            registry=self.root / "config/models.json",
            policy=self.root / "docs/CALLBACK_POLICY.md",
            output=self.root / "reports/text",
            inference_lock=self.root / "runtime/inference",
        )

    def git(self, *arguments):
        return subprocess.check_output(
            ["git", *arguments], cwd=self.root, stderr=subprocess.PIPE, text=True
        ).strip()

    def test_real_checkout_is_committed_clean_and_reused(self):
        checkout = prepare_checkout(
            self.root, (self.request.dataset, self.request.registry, self.request.policy)
        )
        self.assertEqual(checkout, prepare_checkout(self.root))
        self.assertEqual(
            self.git("rev-parse", "HEAD"),
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip(),
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=checkout, text=True
            ).strip(),
            "",
        )
        self.assertNotEqual(checkout, self.root)

    def test_source_drift_and_ignored_untracked_input_are_rejected(self):
        self.request.registry.write_text('{"changed":true}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Commit or set aside"):
            prepare_checkout(self.root)
        self.git("checkout", "--", "config/models.json")
        secret_input = self.root / ".env"
        secret_input.write_text("SECRET=fixture", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "tracked"):
            prepare_checkout(self.root, (secret_input,))

    def test_dirty_reused_checkout_is_rejected(self):
        checkout = prepare_checkout(self.root)
        (checkout / "untracked.txt").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "expected clean"):
            prepare_checkout(self.root)

    def test_launch_binds_source_environment_output_and_shared_lock(self):
        calls = []
        actual_run = subprocess.run

        def capture(command, **kwargs):
            if "voice_callback.evaluation_worker" in command:
                calls.append((command, kwargs))
                return subprocess.CompletedProcess(command, 0)
            return actual_run(command, **kwargs)

        (self.root / ".env").write_text("LANGFUSE_SECRET_KEY=fixture-secret\n", encoding="utf-8")
        with (
            patch("voice_callback.evaluation_workflow.subprocess.run", side_effect=capture),
            contextlib.redirect_stderr(io.StringIO()) as output,
        ):
            self.assertEqual(run_development(self.request), 0)
        command, options = calls[0]
        self.assertEqual(options["env"]["PYTHONPATH"], str(options["cwd"] / "src"))
        self.assertEqual(options["env"]["VCR_LANGFUSE_ENABLED"], "0")
        self.assertEqual(command[command.index("--output-dir") + 1], str(self.request.output))
        self.assertEqual(
            command[command.index("--inference-lock-dir") + 1], str(self.request.inference_lock)
        )
        self.assertNotIn("fixture-secret", " ".join(command) + output.getvalue())
        self.assertEqual(command[command.index("--split") + 1], "development")

    def test_prepare_only_starts_no_worker_or_telemetry(self):
        with (
            patch(
                "voice_callback.evaluation_workflow._worker_command",
                side_effect=AssertionError("worker started"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(run_development(replace(self.request, prepare_only=True)), 0)

    def test_incompatible_baseline_is_rejected_before_checkout_or_worker(self):
        request = replace(self.request, baseline=self.root / "missing")
        with patch(
            "voice_callback.evaluation_workflow.prepare_checkout",
            side_effect=AssertionError("checkout started"),
        ):
            with self.assertRaises(OSError):
                run_development(request)

    def test_cli_dispatches_to_one_workflow_and_offline_history_needs_no_model(self):
        with (
            patch("voice_callback.evaluation_workflow.repository_root", return_value=self.root),
            patch("voice_callback.evaluation_workflow.run_development", return_value=0) as launch,
        ):
            self.assertEqual(
                main(
                    [
                        "evaluate",
                        "--model",
                        "fixture",
                        "--no-trace",
                        "--inference-lock-dir",
                        str(self.request.inference_lock),
                    ]
                ),
                0,
            )
        self.assertEqual(launch.call_args.args[0].tracing, False)
        with (
            patch(
                "voice_callback.cli.OllamaClient",
                side_effect=AssertionError("model client created"),
            ),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(
                main(["evaluations", "--output-dir", str(self.root / "reports"), "--json"]), 0
            )
        self.assertEqual(json.loads(output.getvalue()), {"evaluations": []})

    def test_worker_errors_are_safe_and_held_out_is_rejected(self):
        from voice_callback.evaluation_worker import main as worker_main

        with (
            patch(
                "voice_callback.evaluation_worker.execute_development",
                side_effect=OSError("private path"),
            ),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(worker_main(["evaluate", "--model", "fixture"]), 1)
        self.assertNotIn("private path", output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            worker_main(["evaluate", "--split", "evaluation", "--model", "fixture"])
        for option in ("--prepare-only", "--trace", "--no-trace", "--metadata-only"):
            with (
                patch("voice_callback.evaluation_worker.execute_development") as execute,
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                worker_main(["evaluate", "--model", "fixture", option])
            execute.assert_not_called()
