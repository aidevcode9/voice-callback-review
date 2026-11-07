"""Typed evaluation artifacts; integrity and lifecycle checks remain in the evaluator."""

from typing import Annotated, Literal

from pydantic import Field

from .contracts import (
    Contract,
    Count,
    Digest,
    Explanation,
    ModelEntry,
    Nonempty,
    SchemaVersion,
)
from .domain import FailureCode, Outcome

Split = Literal["development", "evaluation"]


class SourceIdentity(Contract):
    source_sha256: Digest
    git_revision: str | None
    working_tree_clean: bool


class ValidationIdentity(Contract):
    contract_version: Literal["callback-contract-v1"]
    pydantic_version: Nonempty
    pydantic_core_version: Nonempty


class SystemConfiguration(Contract):
    schema_version: SchemaVersion
    model: ModelEntry
    model_digest: Nonempty
    model_metadata_sha256: Digest
    runtime_version: Nonempty
    runtime_url: Nonempty
    diagnostic_timeout: Annotated[float, Field(gt=0, le=30)]
    inference_timeout: Annotated[float, Field(gt=0, le=600)]
    prompt_version: Nonempty
    prompt_sha256: Digest
    policy_version: Nonempty
    policy_sha256: Digest
    code: SourceIdentity
    validation: ValidationIdentity


class EvaluationDeclaration(Contract):
    schema_version: SchemaVersion
    evaluation_id: Nonempty
    split: Split
    dataset_version: Nonempty
    dataset_manifest_sha256: Digest
    inputs_sha256: Digest
    started_at: Nonempty


class InferenceComplete(Contract):
    schema_version: SchemaVersion
    evaluation_id: Nonempty
    count: Count
    system_sha256: Digest
    predictions_sha256: Digest


class AbortedEvaluation(Contract):
    status: Literal["incomplete"]
    completed_predictions: Count


class RatioRecord(Contract):
    numerator: Count
    denominator: Count
    value: Annotated[float, Field(ge=0, le=1)] | None


class Metrics(Contract):
    strict_callback_recall: RatioRecord
    callback_precision: RatioRecord
    needs_review_rate: RatioRecord
    valid_output_coverage: RatioRecord


class WrongDecision(Contract):
    case_id: Nonempty
    expected_label: Outcome
    reference_rationale: Nonempty
    run_id: Nonempty
    predicted_label: Outcome
    reason: Explanation
    evidence: tuple[Explanation, ...]


class ProcessingFailure(Contract):
    case_id: Nonempty
    expected_label: Outcome
    reference_rationale: Nonempty
    run_id: Nonempty
    predicted_label: None
    failure_code: FailureCode
    failure_message: Explanation


class ScoreRecord(Contract):
    total: Count
    valid_outputs: Count
    correct_outputs: Count
    confusion_matrix: dict[Outcome, dict[Outcome, Count]]
    processing_failures_by_expected: dict[Outcome, Count]
    failure_codes: dict[FailureCode, Count]
    metrics: Metrics
    unsafe_misses: tuple[Nonempty, ...]
    disagreements: tuple[WrongDecision | ProcessingFailure, ...]


class ScoreDefinitions(Contract):
    confusion_matrix: Nonempty
    strict_callback_recall: Nonempty
    callback_precision: Nonempty
    needs_review_rate: Nonempty
    valid_output_coverage: Nonempty
    undefined: Nonempty


class EvaluationReport(Contract):
    schema_version: SchemaVersion
    evaluation_id: Nonempty
    split: Split
    dataset_version: Nonempty
    dataset_manifest_sha256: Digest
    inputs_sha256: Digest
    answers_sha256: Digest
    predictions_sha256: Digest
    system_sha256: Digest
    trial_count: Annotated[int, Field(ge=1, le=1)]
    score_version: Literal["callback-score-v1"]
    score: ScoreRecord
    definitions: ScoreDefinitions
    limitations: tuple[Nonempty, ...]


class FrozenConfiguration(Contract):
    schema_version: SchemaVersion
    kind: Literal["frozen_callback_system"]
    system: SystemConfiguration
    system_sha256: Digest
    dataset_manifest_sha256: Digest
    development_evaluation_id: Nonempty
    development_report_sha256: Digest
    frozen_revision: Nonempty
