"""Exact local system identity and explicit candidate configuration freezing."""

import json
import subprocess
from hashlib import sha256
from pathlib import Path

from .classify import (
    POLICY_SHA256,
    PROMPT_VERSION,
    build_classification_request,
    verify_classifier_runtime,
)
from .datasets import DatasetSplit, object_value
from .domain import FailureCode, JsonValue, ModelConfig, RunFailure, RunResult
from .json_io import parse_json, read_bounded
from .models import list_models
from .ollama import OllamaClient
from .storage import render_json


def digest_json(value: object) -> str:
    return sha256(render_json(value).encode("utf-8")).hexdigest()


def source_identity() -> dict[str, JsonValue]:
    sources = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(Path(__file__).parent.glob("*.py"))
    }
    revision = None
    clean = False
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True, timeout=5
        ).strip()
        clean = not subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True, timeout=5
        ).strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return {
        "source_sha256": digest_json(sources),
        "git_revision": revision,
        "working_tree_clean": clean,
    }


def prepare_system(
    dataset: DatasetSplit, model: ModelConfig, client: OllamaClient, policy_path: Path
) -> dict[str, JsonValue]:
    policy = read_bounded(policy_path)
    if sha256(policy).hexdigest() != POLICY_SHA256:
        raise ValueError("Evaluation requires the accepted policy hash.")
    request = build_classification_request(dataset.transcripts[0], model, policy)
    version = client.version()
    choice = list_models((model,), client.installed_models())[0]
    if not choice.selectable or choice.digest is None:
        raise ValueError("Provision the explicitly selected local classifier before evaluation.")
    metadata = client.show(model.model_id)
    verify_classifier_runtime(version, metadata, model.settings["num_ctx"])
    metadata_digest = sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
    return {
        "schema_version": 1,
        "model": object_value(parse_json(render_json(model))),
        "model_digest": choice.digest,
        "model_metadata_sha256": metadata_digest,
        "runtime_version": version,
        "runtime_url": client.base_url,
        "diagnostic_timeout": client.timeout,
        "inference_timeout": client.inference_timeout,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": request.prompt_sha256,
        "policy_version": "1.0",
        "policy_sha256": POLICY_SHA256,
        "code": source_identity(),
    }


def verify_run_system(result: RunResult, system: dict[str, JsonValue]) -> None:
    if isinstance(result, RunFailure) and result.failure.code == FailureCode.CONFIGURATION:
        raise ValueError(
            "Classifier configuration failed during evaluation; results remain unscored."
        )
    provenance = result.provenance
    actual = {
        "model": object_value(parse_json(render_json(provenance.model))),
        "model_digest": provenance.model_digest,
        "model_metadata_sha256": provenance.model_metadata_sha256,
        "runtime_version": None
        if provenance.runtime_version == "unknown"
        else provenance.runtime_version,
        "runtime_url": provenance.runtime_url,
        "prompt_version": provenance.prompt_version,
        "prompt_sha256": provenance.prompt_sha256,
        "policy_version": provenance.policy_version,
        "policy_sha256": provenance.policy_sha256,
    }
    if any(value is not None and value != system[key] for key, value in actual.items()):
        raise ValueError(
            "Classifier configuration drifted during evaluation; no uniform-system report is valid."
        )


def verify_frozen(
    frozen: dict[str, JsonValue], system: dict[str, JsonValue], dataset: DatasetSplit
) -> None:
    code = object_value(system.get("code"))
    original = object_value(frozen.get("system"))
    comparable = {key: value for key, value in system.items() if key != "code"}
    original_comparable = {key: value for key, value in original.items() if key != "code"}
    if (
        frozen.get("schema_version") != 1
        or frozen.get("kind") != "frozen_callback_system"
        or frozen.get("system_sha256") != digest_json(original)
        or frozen.get("dataset_manifest_sha256") != dataset.manifest_sha256
        or frozen.get("frozen_revision") != code.get("git_revision")
        or code.get("working_tree_clean") is not True
        or object_value(original.get("code")).get("source_sha256") != code.get("source_sha256")
        or comparable != original_comparable
    ):
        raise ValueError(
            "Held-out inference requires an unchanged frozen system, dataset, and clean code revision."
        )
