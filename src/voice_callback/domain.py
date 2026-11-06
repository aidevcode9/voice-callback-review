"""Model-independent values. A processing failure never contains a policy label."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool
JsonValue: TypeAlias = JsonScalar | None | list["JsonValue"] | dict[str, "JsonValue"]


class Stage(str, Enum):
    CLASSIFICATION = "classification"
    TRANSCRIPTION = "transcription"


class Runtime(str, Enum):
    OLLAMA = "ollama"
    FASTER_WHISPER = "faster-whisper"


class Outcome(str, Enum):
    CALLBACK_REQUIRED = "callback_required"
    NO_CALLBACK = "no_callback"
    NEEDS_REVIEW = "needs_review"


class TranscriptOrigin(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    CORRECTION = "correction"


class FailureCode(str, Enum):
    CONFIGURATION = "configuration"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    HTTP_ERROR = "http_error"
    INVALID_RESPONSE = "invalid_response"
    MODEL_MISSING = "model_missing"
    INVALID_OUTPUT = "invalid_output"
    INVALID_INPUT = "invalid_input"
    AUDIO_ERROR = "audio_error"
    GPU_MEMORY = "gpu_memory"


@dataclass(frozen=True)
class Failure:
    code: FailureCode
    message: str


@dataclass(frozen=True)
class TranscriptVersion:
    case_id: str
    version_id: str
    text: str
    origin: TranscriptOrigin
    parent_version_id: str | None = None

    @property
    def text_sha256(self) -> str:
        return sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ModelConfig:
    id: str
    runtime: Runtime
    model_id: str
    stages: tuple[Stage, ...]
    settings: Mapping[str, JsonScalar] = field(default_factory=lambda: dict[str, JsonScalar]())

    def __post_init__(self):
        object.__setattr__(self, "settings", MappingProxyType(dict(self.settings)))


@dataclass(frozen=True)
class CallbackDecision:
    label: Outcome
    rule_ids: tuple[str, ...]
    reason: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class RunProvenance:
    run_id: str
    stage: Stage
    model: ModelConfig
    model_digest: str | None
    runtime_version: str
    transcript_version_id: str
    transcript_sha256: str
    prompt_version: str | None
    prompt_sha256: str | None
    policy_version: str | None
    policy_sha256: str | None
    started_at: str
    elapsed_seconds: float
    case_id: str = ""
    runtime_url: str | None = None
    model_metadata_sha256: str | None = None
    request_sha256: str | None = None


@dataclass(frozen=True)
class RunSuccess:
    provenance: RunProvenance
    output: CallbackDecision | TranscriptVersion


@dataclass(frozen=True)
class RunFailure:
    provenance: RunProvenance
    failure: Failure


RunResult = RunSuccess | RunFailure
