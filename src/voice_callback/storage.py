"""Exclusive local records with strict validation at the serialization boundary."""

import json
from dataclasses import fields, is_dataclass
from pathlib import Path

from .contracts import RUN_RECORD, Contract, validate_contract, validate_record
from .domain import ModelConfig, RunResult, RunSuccess
from .json_io import parse_json


def _json_value(value: object) -> object:
    if isinstance(value, ModelConfig):
        return {
            "id": value.id,
            "runtime": value.runtime,
            "model_id": value.model_id,
            "stages": value.stages,
            "settings": dict(value.settings),
        }
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: getattr(value, field.name) for field in fields(value)}
    raise TypeError("Unsupported run record value.")


def render_json(value: object) -> str:
    return (
        json.dumps(
            value,
            default=_json_value,
            ensure_ascii=True,
            allow_nan=False,
            indent=2,
        )
        + "\n"
    )


def render_run(result: RunResult) -> str:
    content = render_json(
        {
            "status": "success" if isinstance(result, RunSuccess) else "processing_error",
            "run": result,
        }
    )
    validate_record(RUN_RECORD, parse_json(content))
    return content


def write_json(path: Path, value: object, contract: type[Contract]) -> None:
    content = render_json(value)
    validate_contract(contract, parse_json(content))
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def save_run(result: RunResult, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{result.provenance.run_id}.json"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(render_run(result))
    return path
