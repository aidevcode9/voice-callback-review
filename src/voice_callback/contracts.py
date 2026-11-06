"""Strict external contracts; JSON schemas and validation share these definitions."""

import json
from typing import Annotated, Literal, TypeVar

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from .domain import FailureCode, JsonScalar, JsonValue, Outcome, Runtime, Stage, TranscriptOrigin


def nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("Expected a nonempty string.")
    return value


def without_whitespace(value: str) -> str:
    if any(char.isspace() for char in value):
        raise ValueError("Identifiers cannot contain whitespace.")
    return value


Nonempty = Annotated[str, StringConstraints(min_length=1, pattern=r"\S"), AfterValidator(nonblank)]
Identifier = Annotated[
    Nonempty, StringConstraints(pattern=r"^\S+$"), AfterValidator(without_whitespace)
]
CaseId = Annotated[Nonempty, Field(max_length=120)]
Explanation = Annotated[Nonempty, Field(max_length=1200)]
Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Count = Annotated[int, Field(ge=0)]
SchemaVersion = Annotated[int, Field(ge=1, le=1)]
RuleId = Literal["UR-001", "CB-002", "CB-003", "NC-001", "NC-002", "NC-003", "NR-001"]
RULE_OUTCOMES: dict[RuleId, Outcome] = {
    "UR-001": Outcome.CALLBACK_REQUIRED,
    "CB-002": Outcome.CALLBACK_REQUIRED,
    "CB-003": Outcome.CALLBACK_REQUIRED,
    "NC-001": Outcome.NO_CALLBACK,
    "NC-002": Outcome.NO_CALLBACK,
    "NC-003": Outcome.NO_CALLBACK,
    "NR-001": Outcome.NEEDS_REVIEW,
}


class Contract(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="forbid", frozen=True, allow_inf_nan=False, hide_input_in_errors=True
    )


class ClassifierSettings(Contract):
    num_ctx: Annotated[int, Field(ge=2048, le=16384)]
    num_predict: Annotated[int, Field(ge=64, le=2048)]
    temperature: Annotated[int | float, Field(ge=0, le=2)]
    seed: Annotated[int, Field(ge=0, le=2147483647)]
    think: bool
    keep_alive: Annotated[int, Field(ge=0, le=0)]

    @model_validator(mode="after")
    def without_thinking(self) -> "ClassifierSettings":
        if self.think:
            raise ValueError("This classifier requires think false.")
        return self


class ModelEntry(Contract):
    id: Identifier
    runtime: Runtime
    model_id: Identifier
    stages: Annotated[tuple[Stage, ...], Field(min_length=1)]
    settings: dict[str, JsonScalar]

    @model_validator(mode="after")
    def local_capabilities(self) -> "ModelEntry":
        if "cloud" in self.model_id.lower() or "://" in self.model_id:
            raise ValueError("Cloud model entries and remote URLs are not supported.")
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("Stage capabilities must be unique.")
        if self.runtime == Runtime.FASTER_WHISPER and self.stages != (Stage.TRANSCRIPTION,):
            raise ValueError("faster-whisper supports only transcription.")
        return self


class ModelRegistry(Contract):
    schema_version: SchemaVersion
    models: tuple[ModelEntry, ...]

    @model_validator(mode="after")
    def unique_ids(self) -> "ModelRegistry":
        if len({model.id for model in self.models}) != len(self.models):
            raise ValueError("Model configuration IDs must be unique.")
        return self


class TranscriptInput(Contract):
    case_id: CaseId
    transcript: str


class CallbackOutput(Contract):
    label: Outcome
    rule_ids: Annotated[
        tuple[RuleId, ...],
        Field(min_length=1, max_length=7, json_schema_extra={"uniqueItems": True}),
    ]
    reason: Explanation
    evidence: Annotated[
        tuple[Explanation, ...],
        Field(min_length=1, max_length=5, json_schema_extra={"uniqueItems": True}),
    ]

    @model_validator(mode="after")
    def supporting_rules_and_unique_quotes(self) -> "CallbackOutput":
        if len(self.rule_ids) != len(set(self.rule_ids)) or len(self.evidence) != len(
            set(self.evidence)
        ):
            raise ValueError("Rules and evidence must be unique.")
        if any(RULE_OUTCOMES[rule] != self.label for rule in self.rule_ids):
            raise ValueError("Rules must support the selected outcome.")
        return self


class FailureOutput(Contract):
    code: FailureCode
    message: Explanation


class TranscriptOutput(Contract):
    case_id: CaseId
    version_id: CaseId
    text: str
    origin: TranscriptOrigin
    parent_version_id: str | None


class Provenance(Contract):
    run_id: Nonempty
    stage: Stage
    model: ModelEntry
    model_digest: str | None
    runtime_version: Nonempty
    transcript_version_id: str
    transcript_sha256: Digest
    prompt_version: str | None
    prompt_sha256: Digest | None
    policy_version: str | None
    policy_sha256: Digest | None
    started_at: Nonempty
    elapsed_seconds: Annotated[float, Field(ge=0)]
    case_id: str
    runtime_url: str | None
    model_metadata_sha256: Digest | None
    request_sha256: Digest | None


class SuccessfulRun(Contract):
    provenance: Provenance
    output: CallbackOutput | TranscriptOutput


class FailedRun(Contract):
    provenance: Provenance
    failure: FailureOutput


class RunSuccessRecord(Contract):
    status: Literal["success"]
    run: SuccessfulRun


class RunFailureRecord(Contract):
    status: Literal["processing_error"]
    run: FailedRun


RUN_RECORD = TypeAdapter(
    Annotated[RunSuccessRecord | RunFailureRecord, Field(discriminator="status")]
)


class PredictionIdentity(Contract):
    case_id: CaseId
    transcript_sha256: Digest
    run_id: Nonempty
    run_sha256: Digest


class SuccessfulPrediction(PredictionIdentity):
    status: Literal["success"]
    output: CallbackOutput


class FailedPrediction(PredictionIdentity):
    status: Literal["processing_error"]
    failure: FailureOutput


PREDICTION_RECORD = TypeAdapter(
    Annotated[SuccessfulPrediction | FailedPrediction, Field(discriminator="status")]
)

Model = TypeVar("Model", bound=Contract)


def validate_contract(model: type[Model], value: JsonValue) -> Model:
    # The caller first uses json_io to reject duplicate keys and non-finite JSON.
    # JSON mode permits JSON arrays/enums without relaxing strict scalar types.
    try:
        return model.model_validate_json(json.dumps(value, allow_nan=False), strict=True)
    except ValidationError:
        raise ValueError(f"{model.__name__} failed contract validation.") from None


def validate_record(adapter: TypeAdapter[Model], value: JsonValue) -> Model:
    try:
        return adapter.validate_json(json.dumps(value, allow_nan=False), strict=True)
    except ValidationError:
        raise ValueError("Saved run or prediction failed contract validation.") from None


def callback_schema() -> dict[str, JsonValue]:
    schema: JsonValue = json.loads(json.dumps(CallbackOutput.model_json_schema()))
    if not isinstance(schema, dict):
        raise ValueError("Expected an object response schema.")
    return schema
