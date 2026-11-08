"""Strict, bounded workspace requests and stored records."""

from typing import Annotated, Literal

from pydantic import Field, field_validator

from .classify import MAX_TRANSCRIPT_BYTES
from .contracts import Contract, Digest, ModelEntry, nonblank
from .evaluation_contracts import SourceIdentity

LocalId = Annotated[str, Field(pattern=r"^[a-z0-9-]{1,64}$")]
Decision = Literal["callback_required", "no_callback", "needs_review"]


class TranscriptText(Contract):
    text: str

    @field_validator("text")
    @classmethod
    def bounded_text(cls, value: str) -> str:
        nonblank(value)
        if len(value.encode("utf-8")) > MAX_TRANSCRIPT_BYTES:
            raise ValueError("Transcript exceeds the UTF-8 byte limit.")
        return value


class CreateCase(TranscriptText):
    title: Annotated[str, Field(min_length=1, max_length=120)] = "Pasted transcript"


class CreateVersion(TranscriptText):
    parent_version_id: LocalId


class SubmitJob(Contract):
    case_id: LocalId
    transcript_version_id: LocalId
    model_config_id: Annotated[str, Field(min_length=1, max_length=120)]


class CreateReview(Contract):
    decision: Decision
    note: str = ""

    @field_validator("note")
    @classmethod
    def bounded_note(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 2000:
            raise ValueError("Review note exceeds the UTF-8 byte limit.")
        return value


class CaseRecord(Contract):
    id: LocalId
    title: str
    created_at: str
    current_version_id: LocalId


class CaseSummary(CaseRecord):
    latest_job_id: LocalId | None = None
    processing_status: Literal["running", "succeeded", "failed", "interrupted"] | None = None
    outcome: Decision | None = None
    human_reviewed: bool = False


class VersionSummary(Contract):
    id: LocalId
    case_id: LocalId
    parent_version_id: LocalId | None
    text_sha256: Digest
    origin: Literal["pasted", "correction", "fictional_development"]
    created_at: str
    development_case_id: LocalId | None = None


class VersionRecord(VersionSummary):
    text: str


class DevelopmentCase(Contract):
    id: LocalId
    title: str
    text: str


class EmptyRequest(Contract):
    pass


class JobRecord(Contract):
    id: LocalId
    case_id: LocalId
    transcript_version_id: LocalId
    model: ModelEntry
    source: SourceIdentity
    status: Literal["running", "succeeded", "failed", "interrupted"]
    created_at: str
    finished_at: str | None = None
    run_id: str | None = None
    error: str | None = None


class ReviewRecord(Contract):
    id: LocalId
    run_id: str
    transcript_version_id: LocalId
    reviewer: Literal["local_owner"] = "local_owner"
    decision: Decision
    note: str
    created_at: str


class CreatedCase(Contract):
    case: CaseRecord
    version: VersionRecord


class CaseDetail(Contract):
    case: CaseRecord
    versions: tuple[VersionSummary, ...]
    jobs: tuple[JobRecord, ...]


class ModelAvailability(Contract):
    id: str
    model_id: str
    stages: tuple[Literal["classification", "transcription"], ...]
    availability: str
    selectable: bool
    digest: str | None


class RuntimeReport(Contract):
    status: Literal["available", "unavailable"]
    server_version: str | None
    models: tuple[ModelAvailability, ...]
    inference_verified: Literal[False] = False
    admission: Literal["ready", "busy", "recovery_required"]
    verification_mode: Literal["live", "controlled"]


class DevelopmentSummary(Contract):
    id: LocalId
    title: str


class Session(Contract):
    nonce: str
