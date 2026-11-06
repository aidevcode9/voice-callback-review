"""Strict bounded JSON boundaries shared by transcript and evaluation artifacts."""

import json
import math
from pathlib import Path

from .domain import JsonValue


def read_bounded(path: Path, limit: int = 1024 * 1024) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("File exceeds its size limit.")
    return raw


def _unique_object(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    value: dict[str, JsonValue] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON fields are not allowed.")
        value[key] = item
    return value


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON numbers are not allowed.")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number exceeds the finite range.")
    return number


def parse_json(text: str) -> JsonValue:
    try:
        value: JsonValue = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except RecursionError:
        raise ValueError("JSON nesting exceeds the supported limit.") from None
    return value


def parse_jsonl(raw: bytes) -> tuple[JsonValue, ...]:
    return tuple(parse_json(line) for line in raw.decode("utf-8").removesuffix("\n").split("\n"))
