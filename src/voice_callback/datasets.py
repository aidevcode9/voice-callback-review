"""Validate frozen split metadata and inputs; answers are a separate explicit read."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .classify import parse_transcripts
from .domain import JsonValue, Outcome, TranscriptVersion
from .json_io import parse_json, parse_jsonl, read_bounded
from .scoring import ReferenceAnswer


def object_value(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return value


def string_value(value: JsonValue) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonempty string.")
    return value


def file_digest(manifest: dict[str, JsonValue], name: str) -> str:
    entry = object_value(object_value(manifest.get("files")).get(name))
    digest = string_value(entry.get("sha256"))
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("Dataset file hash is invalid.")
    return digest


@dataclass(frozen=True)
class DatasetSplit:
    root: Path
    name: str
    version: str
    manifest_sha256: str
    inputs_sha256: str
    answers_sha256: str
    input_bytes: bytes
    transcripts: tuple[TranscriptVersion, ...]


def load_split(root: Path, split: str) -> DatasetSplit:
    if split not in {"development", "evaluation"}:
        raise ValueError("Choose development or evaluation explicitly.")
    raw = read_bounded(root / "manifest.json")
    manifest = object_value(parse_json(raw.decode("utf-8")))
    if manifest.get("status") != "frozen":
        raise ValueError("Evaluation requires a frozen dataset.")
    version = string_value(manifest.get("dataset_version"))
    ids = object_value(manifest.get("splits")).get(split)
    if not isinstance(ids, list) or not ids or any(not isinstance(item, str) for item in ids):
        raise ValueError("Frozen split IDs are invalid.")
    input_digest = file_digest(manifest, f"inputs/{split}.jsonl")
    answers_digest = file_digest(manifest, f"answers/{split}.jsonl")
    inputs = read_bounded(root / "inputs" / f"{split}.jsonl")
    if sha256(inputs).hexdigest() != input_digest:
        raise ValueError("Dataset input hash differs from its manifest.")
    transcripts = parse_transcripts(inputs)
    if len(transcripts) != len(ids) or {row.case_id for row in transcripts} != set(ids):
        raise ValueError("Dataset input coverage differs from its frozen split.")
    return DatasetSplit(
        root,
        split,
        version,
        sha256(raw).hexdigest(),
        input_digest,
        answers_digest,
        inputs,
        transcripts,
    )


def load_answers(dataset: DatasetSplit) -> tuple[ReferenceAnswer, ...]:
    raw = read_bounded(dataset.root / "answers" / f"{dataset.name}.jsonl")
    if sha256(raw).hexdigest() != dataset.answers_sha256:
        raise ValueError("Answer hash differs from the frozen manifest.")
    answers: list[ReferenceAnswer] = []
    for value in parse_jsonl(raw):
        row = object_value(value)
        if set(row) != {"case_id", "expected_label", "rationale", "rule_ids", "evidence"}:
            raise ValueError("Answer schema is invalid.")
        answers.append(
            ReferenceAnswer(
                string_value(row["case_id"]),
                Outcome(row["expected_label"]),
                string_value(row["rationale"]),
            )
        )
    ids = [row.case_id for row in answers]
    if len(set(ids)) != len(ids) or set(ids) != {row.case_id for row in dataset.transcripts}:
        raise ValueError("Answers must cover the frozen split exactly once.")
    return tuple(answers)
