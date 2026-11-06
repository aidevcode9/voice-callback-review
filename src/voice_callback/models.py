"""Explicit capability registry joined with observed installation, never inferred selection."""

from dataclasses import dataclass
from pathlib import Path

from .contracts import ModelRegistry, validate_contract
from .domain import ModelConfig, Runtime, Stage
from .json_io import parse_json, read_bounded
from .ollama import InstalledModel


@dataclass(frozen=True)
class ModelAvailability:
    config: ModelConfig
    status: str
    digest: str | None
    selectable: bool


def load_registry(path: Path) -> tuple[ModelConfig, ...]:
    try:
        registry = validate_contract(ModelRegistry, parse_json(read_bounded(path).decode("utf-8")))
        return tuple(
            ModelConfig(row.id, row.runtime, row.model_id, row.stages, row.settings)
            for row in registry.models
        )
    except (OSError, ValueError, TypeError, RecursionError):
        raise ValueError(
            "Invalid model registry; use explicit local model entries without defaults."
        ) from None


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
