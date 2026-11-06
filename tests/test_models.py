"""Registry, stage selection, and provenance behavior without weights or inference."""

import json
import tempfile
import unittest
from collections.abc import MutableMapping
from dataclasses import replace
from pathlib import Path
from typing import cast

from voice_callback.domain import (
    Failure,
    FailureCode,
    JsonScalar,
    ModelConfig,
    Outcome,
    RunFailure,
    RunProvenance,
    Runtime,
    Stage,
    TranscriptOrigin,
    TranscriptVersion,
)
from voice_callback.models import list_models, load_registry
from voice_callback.ollama import InstalledModel

ROOT = Path(__file__).resolve().parents[1]


class ModelRegistryBehavior(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".test-work"
        scratch.mkdir(exist_ok=True)
        folder = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "models.json"
        self.row = {
            "id": "classifier-candidate",
            "runtime": "ollama",
            "model_id": "example:4b",
            "stages": ["classification"],
            "settings": {"temperature": 0},
        }

    def registry(self, rows):
        self.path.write_text(json.dumps({"schema_version": 1, "models": rows}), encoding="utf-8")
        return load_registry(self.path)

    def test_shipped_registry_has_owner_selected_classifier_and_planned_transcription(self):
        configs = load_registry(ROOT / "config/models.json")
        self.assertEqual(
            {c.model_id for c in configs}, {"qwen3.5:4b-q4_K_M", "large-v3-turbo", "small"}
        )
        choices = list_models(configs, (), Stage.CLASSIFICATION)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].status, "not_installed")
        self.assertTrue(all(not choice.selectable for choice in list_models(configs, ())))

    def test_configured_and_installed_must_both_match_exact_identity(self):
        configs = self.registry([self.row])
        self.assertEqual(list_models(configs, ())[0].status, "not_installed")
        self.assertEqual(list_models(configs, None)[0].status, "installation_unknown")
        observed = (InstalledModel("example:4b", "abc"), InstalledModel("other:latest", "def"))
        choice = list_models(configs, observed, Stage.CLASSIFICATION)[0]
        self.assertTrue(choice.selectable)
        self.assertEqual(choice.digest, "abc")
        self.assertEqual(len(list_models(configs, observed)), 1)
        self.assertEqual(list_models(configs, observed, Stage.TRANSCRIPTION), ())
        self.assertFalse(
            list_models(configs, (InstalledModel("example:latest", "abc"),))[0].selectable
        )

    def test_observed_remote_model_is_never_selectable(self):
        configs = self.registry([self.row])
        choice = list_models(configs, (InstalledModel("example:4b", "abc", remote=True),))[0]
        self.assertFalse(choice.selectable)
        self.assertEqual(choice.status, "remote_not_supported")

    def test_ollama_transcription_is_not_an_implemented_adapter(self):
        configs = self.registry([{**self.row, "stages": ["transcription"]}])
        choice = list_models(configs, (InstalledModel("example:4b", "abc"),), Stage.TRANSCRIPTION)[
            0
        ]
        self.assertEqual(choice.status, "adapter_not_implemented")
        self.assertFalse(choice.selectable)

    def test_ollama_installation_never_proves_whisper_installation(self):
        configs = load_registry(ROOT / "config/models.json")
        choices = list_models(
            configs, (InstalledModel("small", "ollama-digest"),), Stage.TRANSCRIPTION
        )
        self.assertTrue(
            all(c.status == "runtime_not_verified" and c.digest is None for c in choices)
        )

    def test_invalid_registry_is_rejected(self):
        invalid_rows = [
            [self.row, self.row],
            [{**self.row, "stages": []}],
            [{**self.row, "stages": ["classification", "classification"]}],
            [{**self.row, "stages": ["unknown"]}],
            [{**self.row, "runtime": "cloud"}],
            [{**self.row, "model_id": "example:cloud"}],
            [{**self.row, "model_id": "https://example.com"}],
            [{**self.row, "runtime": "faster-whisper"}],
            [{**self.row, "settings": []}],
            [{**self.row, "settings": {"temperature": float("nan")}}],
            [{**self.row, "settings": {"nested": {}}}],
            [{**self.row, "default": True}],
            [{**self.row, "id": ""}],
            [{**self.row, "id": 2}],
            [None],
        ]
        for rows in invalid_rows:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.registry(rows)

    def test_bad_json_missing_file_and_defaults_are_rejected(self):
        with self.assertRaises(ValueError):
            load_registry(self.path)
        for value in (
            "not-json",
            "[]",
            '{"schema_version": 2, "models": []}',
            '{"schema_version": 1, "models": [], "default": "x"}',
        ):
            self.path.write_text(value, encoding="utf-8")
            with self.subTest(value=value), self.assertRaises(ValueError):
                load_registry(self.path)


class DomainContracts(unittest.TestCase):
    def test_corrected_transcript_retains_parent_and_exact_text_hash(self):
        original = TranscriptVersion("case", "v1", "Call back.\n", TranscriptOrigin.TEXT)
        corrected = replace(
            original,
            version_id="v2",
            text="Call back!\n",
            origin=TranscriptOrigin.CORRECTION,
            parent_version_id="v1",
        )
        self.assertEqual(original.text, "Call back.\n")
        self.assertEqual(corrected.parent_version_id, original.version_id)
        self.assertNotEqual(original.text_sha256, corrected.text_sha256)
        self.assertNotEqual(original.text_sha256, replace(original, text="Call back.").text_sha256)

    def test_run_model_settings_do_not_change_with_callers_dictionary(self):
        settings = {"temperature": 0}
        model = ModelConfig(
            "candidate", Runtime.OLLAMA, "example:4b", (Stage.CLASSIFICATION,), settings
        )
        settings["temperature"] = 1
        self.assertEqual(model.settings["temperature"], 0)
        with self.assertRaises(TypeError):
            cast(MutableMapping[str, JsonScalar], model.settings)["temperature"] = 2

    def test_failure_does_not_contain_or_masquerade_as_policy_outcome(self):
        model = ModelConfig("candidate", Runtime.OLLAMA, "example:4b", (Stage.CLASSIFICATION,))
        provenance = RunProvenance(
            "run",
            Stage.CLASSIFICATION,
            model,
            None,
            "test",
            "v1",
            "hash",
            None,
            None,
            None,
            None,
            "2026-11-05T00:00:00Z",
            0.1,
        )
        failure = RunFailure(provenance, Failure(FailureCode.TIMEOUT, "Local request timed out."))
        self.assertFalse(hasattr(failure, "label"))
        self.assertFalse(hasattr(failure, "output"))
        self.assertNotIn(failure.failure.code.value, {outcome.value for outcome in Outcome})
