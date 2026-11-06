"""Explicit capability registry joined with observed installation, never inferred selection."""

from dataclasses import dataclass
import json
import math
from pathlib import Path

from .domain import ModelConfig, Runtime, Stage
from .ollama import InstalledModel


@dataclass(frozen=True)
class ModelAvailability:
    config: ModelConfig
    status: str
    digest: str | None
    selectable: bool


def load_registry(path: Path) -> tuple[ModelConfig, ...]:
    try:
        if path.stat().st_size > 1024 * 1024:
            raise ValueError("Model registry exceeds 1 MiB.")
        value = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(value, dict) or set(value) != {"schema_version", "models"}
                or type(value["schema_version"]) is not int or value["schema_version"] != 1
                or not isinstance(value["models"], list)):
            raise ValueError("Expected registry schema_version 1 and a models list; no defaults are supported.")
        configs, ids = [], set()
        for row in value["models"]:
            if not isinstance(row, dict) or set(row) != {"id", "runtime", "model_id", "stages", "settings"}:
                raise ValueError("Each model requires id, runtime, model_id, stages, and settings.")
            for key in ("id", "model_id"):
                if (not isinstance(row[key], str) or not row[key].strip()
                        or any(char.isspace() for char in row[key])):
                    raise ValueError("Model identifiers must be nonempty without whitespace.")
            if row["id"] in ids:
                raise ValueError("Model configuration IDs must be unique.")
            if "cloud" in row["model_id"].lower() or "://" in row["model_id"]:
                raise ValueError("Cloud model entries and remote URLs are not supported.")
            runtime = Runtime(row["runtime"])
            if not isinstance(row["stages"], list) or not row["stages"]:
                raise ValueError("A model needs explicit stage capabilities.")
            stages = tuple(Stage(stage) for stage in row["stages"])
            if len(stages) != len(set(stages)):
                raise ValueError("Stage capabilities must be unique.")
            if runtime == Runtime.FASTER_WHISPER and stages != (Stage.TRANSCRIPTION,):
                raise ValueError("faster-whisper supports only transcription.")
            settings = row["settings"]
            if not isinstance(settings, dict) or any(
                not isinstance(item, (str, int, float, bool))
                or isinstance(item, float) and not math.isfinite(item)
                for item in settings.values()
            ):
                raise ValueError("Settings must contain finite scalar values.")
            configs.append(ModelConfig(row["id"], runtime, row["model_id"], stages,
                                       settings))
            ids.add(row["id"])
        return tuple(configs)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        raise ValueError(f"Invalid model registry: {error}") from None


def list_models(configs: tuple[ModelConfig, ...], installed: tuple[InstalledModel, ...] | None,
                stage: Stage | None = None) -> tuple[ModelAvailability, ...]:
    observed = {model.name: model for model in installed or ()}
    result = []
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
        result.append(ModelAvailability(config, status, model.digest if model else None,
                                        status == "installed_configured"))
    return tuple(result)
