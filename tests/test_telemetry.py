"""Tracing must not change classification or export transcript content."""

import unittest
from unittest.mock import MagicMock, patch

import test_classify
from test_classify import MODEL, ROOT, TEXT, fixtures
from test_ollama import server

from voice_callback.classify import classify
from voice_callback.domain import RunSuccess, TranscriptOrigin, TranscriptVersion
from voice_callback.ollama import OllamaClient


class TelemetryBehavior(unittest.TestCase):
    def test_classification_exports_only_safe_metadata_and_usage(self):
        client, root, generation = MagicMock(), MagicMock(), MagicMock()
        client.start_observation.return_value = root
        root.start_observation.return_value = generation
        routes = fixtures()
        response = routes["/api/chat"][1]
        response.update(prompt_eval_count=100, eval_count=20)
        transcript = TranscriptVersion(
            "private-case", "private-version", TEXT, TranscriptOrigin.TEXT
        )
        environment = {
            "VCR_LANGFUSE_ENABLED": "1",
            "VCR_LANGFUSE_CONTENT": "0",
            "LANGFUSE_PUBLIC_KEY": "public",
            "LANGFUSE_SECRET_KEY": "secret",
            "LANGFUSE_BASE_URL": "https://example.invalid",
        }
        with (
            patch.dict("os.environ", environment),
            patch(
                "voice_callback.telemetry._get_client",
                return_value=client,
            ),
            server(routes, []) as (url, _),
        ):
            result = classify(
                transcript, MODEL, OllamaClient(url), policy_path=ROOT / "docs/CALLBACK_POLICY.md"
            )
        self.assertIsInstance(result, RunSuccess)
        generation.update.assert_any_call(usage_details={"input": 100, "output": 20})
        generation.update.assert_any_call(output={"status": "success"})
        exported = str(client.mock_calls) + str(root.mock_calls) + str(generation.mock_calls)
        self.assertNotIn(TEXT, exported)
        self.assertNotIn("private-case", exported)
        self.assertNotIn("private-version", exported)
        self.assertNotIn("secret", exported)
        client.flush.assert_called_once()

    def test_content_mode_records_transcript_and_validated_answer(self):
        client, root, generation = MagicMock(), MagicMock(), MagicMock()
        client.start_observation.return_value = root
        root.start_observation.return_value = generation
        transcript = TranscriptVersion(
            "private-case", "private-version", TEXT, TranscriptOrigin.TEXT
        )
        env = {
            "VCR_LANGFUSE_ENABLED": "1",
            "VCR_LANGFUSE_CONTENT": "1",
            "LANGFUSE_PUBLIC_KEY": "public",
            "LANGFUSE_SECRET_KEY": "secret",
            "LANGFUSE_BASE_URL": "https://example.invalid",
        }
        with (
            patch.dict("os.environ", env),
            patch("voice_callback.telemetry._get_client", return_value=client),
            server(fixtures(), []) as (url, _),
        ):
            result = classify(
                transcript, MODEL, OllamaClient(url), policy_path=ROOT / "docs/CALLBACK_POLICY.md"
            )
        self.assertIsInstance(result, RunSuccess)
        root.update.assert_any_call(input={"transcript": TEXT})
        expected = {
            "status": "success",
            "label": "callback_required",
            "rule_ids": ["CB-002"],
            "reason": "The caller requests a callback.",
            "evidence": ["Please call me back"],
        }
        root.update.assert_any_call(output=expected)
        generation.update.assert_any_call(output=expected)
        exported = str(client.mock_calls) + str(root.mock_calls) + str(generation.mock_calls)
        self.assertNotIn("private-case", exported)
        self.assertNotIn("private-version", exported)
        self.assertNotIn("secret", exported)

    def test_disabled_and_unavailable_sdk_leave_classification_unchanged(self):
        test = test_classify.ClassificationBehavior()
        test.setUp()
        with patch.dict("os.environ", {"VCR_LANGFUSE_ENABLED": "0"}):
            result, _, _ = test.run_classifier()
        self.assertIsInstance(result, RunSuccess)
        env = {
            "VCR_LANGFUSE_ENABLED": "1",
            "LANGFUSE_PUBLIC_KEY": "p",
            "LANGFUSE_SECRET_KEY": "s",
            "LANGFUSE_BASE_URL": "https://example.invalid",
        }
        with (
            patch.dict("os.environ", env),
            patch("voice_callback.telemetry._get_client", side_effect=ImportError),
        ):
            result, _, _ = test.run_classifier()
        self.assertIsInstance(result, RunSuccess)


if __name__ == "__main__":
    unittest.main()
