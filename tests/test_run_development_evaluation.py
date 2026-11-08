"""The legacy path only adapts arguments to the canonical packaged workflow."""

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts import run_development_evaluation as launcher


class DevelopmentLauncherTests(unittest.TestCase):
    def test_redirects_arguments_and_preserves_exit_status(self):
        args = ["--model", "qwen35-4b", "--metadata-only", "--prepare-only"]
        with (
            patch.object(launcher, "cli_main", return_value=2) as command,
            contextlib.redirect_stderr(io.StringIO()) as output,
        ):
            self.assertEqual(launcher.main(args), 2)
        command.assert_called_once_with(["evaluate", *args])
        self.assertIn("voice-callback evaluate", output.getvalue())
