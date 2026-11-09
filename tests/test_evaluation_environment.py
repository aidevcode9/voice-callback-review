"""Resolve literal local tracing settings without credentials or external services."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from voice_callback.evaluation_environment import ENVIRONMENT_LIMIT, evaluation_environment


class EvaluationEnvironmentTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / ".test-work"
        scratch.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)

    def write_environment(self, content):
        (self.root / ".env").write_text(content, encoding="utf-8-sig")

    def test_disabled_by_default_without_credentials_or_sdk_access(self):
        with patch("importlib.import_module", side_effect=AssertionError("No SDK import")):
            resolved = evaluation_environment(self.root, environment={"PATH": "process-path"})
        self.assertEqual(resolved["VCR_LANGFUSE_ENABLED"], "0")
        self.assertEqual(resolved["LANGFUSE_TRACING_ENABLED"], "false")
        self.assertEqual(resolved["PATH"], "process-path")
        self.assertNotIn("LANGFUSE_SECRET_KEY", resolved)

    def test_allowlisted_file_defaults_support_bom_quotes_export_and_comments(self):
        self.write_environment(
            "# settings\n\n"
            "export LANGFUSE_PUBLIC_KEY='public fixture' # after quote\n"
            'LANGFUSE_SECRET_KEY="literal \\n $HOME $(nothing)"\n'
            "LANGFUSE_BASE_URL=https://example.invalid/path#fragment # comment\n"
            "VCR_LANGFUSE_ENABLED=1\n"
            "VCR_LANGFUSE_CONTENT=0\n"
            "UNRELATED=ignored\n"
            "malformed unrelated setting\n"
        )
        resolved = evaluation_environment(self.root, environment={})
        self.assertEqual(resolved["LANGFUSE_PUBLIC_KEY"], "public fixture")
        self.assertEqual(resolved["LANGFUSE_SECRET_KEY"], "literal \\n $HOME $(nothing)")
        self.assertEqual(resolved["LANGFUSE_BASE_URL"], "https://example.invalid/path#fragment")
        self.assertEqual(resolved["VCR_LANGFUSE_ENABLED"], "1")
        self.assertEqual(resolved["LANGFUSE_TRACING_ENABLED"], "true")
        self.assertEqual(resolved["VCR_LANGFUSE_CONTENT"], "0")
        self.assertNotIn("UNRELATED", resolved)

    def test_process_values_and_explicit_empty_values_override_file_values(self):
        self.write_environment(
            "LANGFUSE_PUBLIC_KEY=file-public\nLANGFUSE_SECRET_KEY=file-secret\n"
            "VCR_LANGFUSE_ENABLED=1\nVCR_LANGFUSE_CONTENT=1\n"
        )
        source = {
            "LANGFUSE_PUBLIC_KEY": "process-public",
            "LANGFUSE_SECRET_KEY": "",
            "VCR_LANGFUSE_ENABLED": "",
            "VCR_LANGFUSE_CONTENT": "",
            "EXISTING_PROCESS_VARIABLE": "retained",
        }
        resolved = evaluation_environment(self.root, environment=source)
        self.assertEqual(resolved["LANGFUSE_PUBLIC_KEY"], "process-public")
        self.assertEqual(resolved["LANGFUSE_SECRET_KEY"], "")
        self.assertEqual(resolved["VCR_LANGFUSE_ENABLED"], "0")
        self.assertEqual(resolved["VCR_LANGFUSE_CONTENT"], "")
        self.assertEqual(resolved["EXISTING_PROCESS_VARIABLE"], "retained")
        self.assertEqual(source["VCR_LANGFUSE_ENABLED"], "")

    def test_default_environment_is_copied_without_mutating_process(self):
        self.write_environment("LANGFUSE_PUBLIC_KEY=file-public\n")
        with patch.dict("os.environ", {"LANGFUSE_PUBLIC_KEY": "process-public"}, clear=True):
            resolved = evaluation_environment(self.root)
            self.assertEqual(resolved["LANGFUSE_PUBLIC_KEY"], "process-public")
            self.assertNotIn("VCR_LANGFUSE_ENABLED", os.environ)

    def test_unicode_separators_remain_literal_value_content(self):
        self.write_environment('LANGFUSE_SECRET_KEY="before\u2028after\u0085end"\n')
        resolved = evaluation_environment(self.root, environment={})
        self.assertEqual(resolved["LANGFUSE_SECRET_KEY"], "before\u2028after\u0085end")

    def test_explicit_tracing_switches_override_file_and_process_without_requiring_keys(self):
        self.write_environment("VCR_LANGFUSE_ENABLED=1\nLANGFUSE_TRACING_ENABLED=true\n")
        disabled = evaluation_environment(self.root, tracing=False, environment={})
        self.assertEqual(disabled["VCR_LANGFUSE_ENABLED"], "0")
        self.assertEqual(disabled["LANGFUSE_TRACING_ENABLED"], "false")
        enabled = evaluation_environment(
            self.root, tracing=True, environment={"VCR_LANGFUSE_ENABLED": "0"}
        )
        self.assertEqual(enabled["VCR_LANGFUSE_ENABLED"], "1")
        self.assertEqual(enabled["LANGFUSE_TRACING_ENABLED"], "true")
        self.assertNotIn("LANGFUSE_SECRET_KEY", enabled)

    def test_metadata_only_overrides_content_without_enabling_tracing(self):
        resolved = evaluation_environment(
            self.root,
            metadata_only=True,
            environment={"VCR_LANGFUSE_CONTENT": "1"},
        )
        self.assertEqual(resolved["VCR_LANGFUSE_CONTENT"], "0")
        self.assertEqual(resolved["VCR_LANGFUSE_ENABLED"], "0")

    def test_enabled_tracing_preserves_an_explicit_sdk_switch(self):
        resolved = evaluation_environment(
            self.root,
            tracing=True,
            environment={"LANGFUSE_TRACING_ENABLED": ""},
        )
        self.assertEqual(resolved["LANGFUSE_TRACING_ENABLED"], "")

    def test_empty_and_duplicate_assignments_have_literal_last_value(self):
        self.write_environment(
            "LANGFUSE_SECRET_KEY=old\nLANGFUSE_SECRET_KEY= # empty\n"
            'export\tLANGFUSE_PUBLIC_KEY = "" # also empty\n'
        )
        resolved = evaluation_environment(self.root, environment={})
        self.assertEqual(resolved["LANGFUSE_SECRET_KEY"], "")
        self.assertEqual(resolved["LANGFUSE_PUBLIC_KEY"], "")

    def test_malformed_recognized_values_report_only_key_and_line(self):
        for malformed in (
            'LANGFUSE_SECRET_KEY="private-fixture',
            "LANGFUSE_SECRET_KEY private-fixture",
            'LANGFUSE_SECRET_KEY="private-fixture" trailing-private-fixture',
            "LANGFUSE_SECRET_KEY=private-fixture\x00",
        ):
            with self.subTest(malformed=malformed):
                self.write_environment("# comment\n" + malformed + "\n")
                with self.assertRaises(ValueError) as caught:
                    evaluation_environment(self.root, environment={})
                self.assertEqual(
                    str(caught.exception),
                    "Invalid .env assignment for LANGFUSE_SECRET_KEY on line 2.",
                )
                self.assertNotIn("private-fixture", str(caught.exception))

    def test_unrelated_malformed_assignments_cannot_inject_or_override_environment(self):
        self.write_environment(
            "PYTHONPATH=\"unterminated\nPATH=/untrusted\nLANGFUSE_SECRET_KEY_OTHER='unrelated\n"
        )
        resolved = evaluation_environment(self.root, environment={"PATH": "trusted"})
        self.assertEqual(resolved["PATH"], "trusted")
        self.assertNotIn("PYTHONPATH", resolved)
        self.assertNotIn("LANGFUSE_SECRET_KEY_OTHER", resolved)

    def test_file_size_and_encoding_fail_without_echoing_content(self):
        for content, message in (
            (b"private-fixture" * ENVIRONMENT_LIMIT, "Root .env exceeds the 64 KiB size limit."),
            (b"LANGFUSE_SECRET_KEY=private-fixture\xff", "Root .env must use UTF-8 encoding."),
        ):
            with self.subTest(message=message):
                (self.root / ".env").write_bytes(content)
                with self.assertRaises(ValueError) as caught:
                    evaluation_environment(self.root, environment={})
                self.assertEqual(str(caught.exception), message)
                self.assertNotIn("private-fixture", str(caught.exception))

    def test_unreadable_environment_file_has_safe_error(self):
        (self.root / ".env").mkdir()
        with self.assertRaisesRegex(ValueError, "Cannot read root .env"):
            evaluation_environment(self.root, environment={})

    def test_legacy_txt_is_not_loaded(self):
        legacy = self.root / ".github/workflows/langfuse.txt"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("LANGFUSE_SECRET_KEY=legacy-fixture\n", encoding="utf-8")
        resolved = evaluation_environment(self.root, environment={})
        self.assertNotIn("LANGFUSE_SECRET_KEY", resolved)


if __name__ == "__main__":
    unittest.main()
