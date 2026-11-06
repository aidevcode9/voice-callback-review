"""Explicit capability registry joined with observed installation, never inferred selection."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

from .domain import JsonScalar, JsonValue, ModelConfig, Runtime, Stage
from .ollama import InstalledModel


@dataclass(frozen=True)
class ModelAvailability:
    config: ModelConfig
    status: str
    digest: str | None
    selectable: bool


def _identifier(value: JsonValue) -> str:
    if not isinstance(value, str) or not value.strip() or any(char.isspace() for char in value):
        raise ValueError("Model identifiers must be nonempty without whitespace.")
    return value


def _model_config(row: JsonValue) -> ModelConfig:
    if not isinstance(row, dict) or set(row) != {"id", "runtime", "model_id", "stages", "settings"}:
        raise ValueError("Each model requires id, runtime, model_id, stages, and settings.")
    config_id = _identifier(row["id"])
    model_id = _identifier(row["model_id"])
    if "cloud" in model_id.lower() or "://" in model_id:
        raise ValueError("Cloud model entries and remote URLs are not supported.")
    runtime = Runtime(row["runtime"])
    stage_values = row["stages"]
    if not isinstance(stage_values, list) or not stage_values:
        raise ValueError("A model needs explicit stage capabilities.")
    stages = tuple(Stage(stage) for stage in stage_values)
    if len(stages) != len(set(stages)):
        raise ValueError("Stage capabilities must be unique.")
    if runtime == Runtime.FASTER_WHISPER and stages != (Stage.TRANSCRIPTION,):
        raise ValueError("faster-whisper supports only transcription.")
    raw_settings = row["settings"]
    if not isinstance(raw_settings, dict):
        raise ValueError("Settings must contain finite scalar values.")
    settings: dict[str, JsonScalar] = {}
    for key, item in raw_settings.items():
        if not isinstance(item, (str, int, float, bool)) or (
            isinstance(item, float) and not math.isfinite(item)
        ):
            raise ValueError("Settings must contain finite scalar values.")
        settings[key] = item
    return ModelConfig(config_id, runtime, model_id, stages, settings)


def load_registry(path: Path) -> tuple[ModelConfig, ...]:
    try:
        if path.stat().st_size > 1024 * 1024:
            raise ValueError("Model registry exceeds 1 MiB.")
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(value, dict)
            or set(value) != {"schema_version", "models"}
            or type(value["schema_version"]) is not int
            or value["schema_version"] != 1
            or not isinstance(value["models"], list)
        ):
            raise ValueError(
                "Expected registry schema_version 1 and a models list; no defaults are supported."
            )
        configs: list[ModelConfig] = []
        ids: set[str] = set()
        for row in value["models"]:
            config = _model_config(row)
            if config.id in ids:
                raise ValueError("Model configuration IDs must be unique.")
            configs.append(config)
            ids.add(config.id)
        return tuple(configs)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        raise ValueError(f"Invalid model registry: {error}") from None


def list_models(
    configs: tuple[ModelConfig, ...],
    installed: tuple[InstalledModel, ...] | None,
    stage: Stage | None = None,
) -> tuple[ModelAvailability, ...]:
    observed = {model.name: model for model in installed or ()}
    result: list[ModelAvailability] = []
    for config in configs:
        if stage is not None and stage not in config.stages:
            continue
        model = observed.get(config.model_id) if config.runtime == Runtime.OLLAMA else None
        if config.runtime != Runtime.OLLAMA:
            status = "runtime_not_verified"
        elif installed is None:
            status = "installation_unknown"
        elif model is None:
            status = "not_installed"
        elif model.remote:
            status = "remote_not_supported"
        elif stage == Stage.TRANSCRIPTION or config.stages == (Stage.TRANSCRIPTION,):
            status = "adapter_not_implemented"
        else:
            status = "installed_configured"
        result.append(
            ModelAvailability(
                config, status, model.digest if model else None, status == "installed_configured"
            )
        )
    return tuple(result)
