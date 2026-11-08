"""Process-boundary regressions without starting or stopping real services."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import local_stack

ROOT = Path(__file__).resolve().parents[1]


class StackOwnership(unittest.TestCase):
    def test_failed_second_launch_never_signals_an_existing_nginx(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-work") as folder:
            root = Path(folder)
            (root / "web/.next").mkdir(parents=True)
            (root / "web/.next/BUILD_ID").write_text("build", encoding="utf-8")
            (root / "runtime").mkdir()
            pid = root / "runtime/nginx.pid"
            pid.write_text("12345", encoding="utf-8")
            config = root / "nginx.conf"
            config.write_text("isolated fixture", encoding="utf-8")
            process = Mock()
            process.poll.return_value = None
            with (
                patch.object(local_stack, "ROOT", root),
                patch.object(local_stack.shutil, "which", return_value="node"),
                patch.object(local_stack, "nginx_executable", return_value="nginx"),
                patch.object(local_stack.signal, "signal"),
                patch.object(local_stack.subprocess, "run") as run,
                patch.object(
                    local_stack.subprocess,
                    "Popen",
                    side_effect=[process, OSError("startup failure")],
                ),
                self.assertRaises(OSError),
            ):
                local_stack.run_stack(["fake-api"], 3000, root, config)
            self.assertFalse(any("-s" in call.args[0] for call in run.call_args_list))
            self.assertEqual(pid.read_text(encoding="utf-8"), "12345")
            process.terminate.assert_called_once()
