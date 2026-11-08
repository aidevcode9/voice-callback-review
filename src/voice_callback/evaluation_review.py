"""Read-only development evaluation review and compatible saved-run comparison.

Saved counts are validated against callback-score-v1. This does not re-execute
historical source or replace the source-compatible ``score_run`` operation.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .contracts import RUN_RECORD, validate_contract, validate_record
from .datasets import DatasetSplit, load_answers, load_split, object_value
from .domain import CallbackDecision, Failure, JsonValue, Outcome, TranscriptVersion
from .evaluate import SCORE_DEFINITIONS, read_document, read_predictions
from .evaluation_config import digest_json
from .evaluation_contracts import (
    EvaluationDeclaration,
    EvaluationReport,
    InferenceComplete,
    RatioRecord,
    ScoreDefinitions,
    ScoreRecord,
    SystemConfiguration,
)
from .json_io import parse_json, read_bounded
from .scoring import Prediction, ReferenceAnswer, score
from .storage import render_json

METRIC_LABELS = {
    "strict_callback_recall": "Callback recall",
    "callback_precision": "Callback precision",
    "needs_review_rate": "Needs-review rate",
    "valid_output_coverage": "Valid-output coverage",
}


@dataclass(frozen=True)
class ReviewedCase:
    transcript: TranscriptVersion
    answer: ReferenceAnswer
    prediction: Prediction

    @property
    def correct(self) -> bool:
        result = self.prediction.result
        return isinstance(result, CallbackDecision) and result.label == self.answer.label

    @property
    def unsafe_miss(self) -> bool:
        result = self.prediction.result
        return (
            self.answer.label == Outcome.CALLBACK_REQUIRED
            and isinstance(result, CallbackDecision)
            and result.label == Outcome.NO_CALLBACK
        )


@dataclass(frozen=True)
class SavedEvaluation:
    directory: Path
    report: EvaluationReport
    system: SystemConfiguration
    dataset: DatasetSplit
    cases: tuple[ReviewedCase, ...]
    report_sha256: str
    verification: str = (
        "Saved snapshot; callback-score-v1 counts validated. Historical source not rerun."
    )


@dataclass(frozen=True)
class MetricChange:
    name: str
    baseline: RatioRecord
    current: RatioRecord
    percentage_points: float | None


@dataclass(frozen=True)
class CaseChange:
    case_id: str
    baseline: ReviewedCase
    current: ReviewedCase
    kind: str


@dataclass(frozen=True)
class Comparison:
    baseline_id: str
    current_id: str
    metrics: tuple[MetricChange, ...]
    cases: tuple[CaseChange, ...]
    fixes: tuple[str, ...]
    regressions: tuple[str, ...]
    new_unsafe_misses: tuple[str, ...]
    removed_unsafe_misses: tuple[str, ...]
    configuration_changes: tuple[str, ...]


def load_review(directory: Path, dataset_root: Path) -> SavedEvaluation:
    """Validate completed saved development artifacts before opening answers."""
    declaration = validate_contract(
        EvaluationDeclaration, read_document(directory / "evaluation.json", EvaluationDeclaration)
    )
    if declaration.split != "development":
        raise ValueError("Development review does not open held-out evaluation artifacts.")
    if (directory / "aborted.json").exists():
        raise ValueError("Incomplete evaluation has no completed quality report.")
    ready = validate_contract(
        InferenceComplete, read_document(directory / "inference-complete.json", InferenceComplete)
    )
    system_document = read_document(directory / "configuration.json", SystemConfiguration)
    system = validate_contract(SystemConfiguration, system_document)
    report_raw = read_bounded(directory / "report.json")
    report = validate_contract(EvaluationReport, parse_json(report_raw.decode("utf-8")))
    dataset = load_split(dataset_root, "development")
    predictions_raw = read_bounded(directory / "predictions.jsonl", 16 * 1024 * 1024)
    _validate_snapshot(
        directory, declaration, ready, system_document, report, dataset, predictions_raw
    )
    predictions = read_predictions(predictions_raw, dataset, directory)
    _validate_run_configuration(directory, predictions, system)
    answers = load_answers(dataset)
    saved_counts = validate_contract(
        ScoreRecord, object_value(parse_json(render_json(score(predictions, answers))))
    )
    if saved_counts != report.score:
        raise ValueError("Saved report counts differ from the validated predictions and answers.")
    expected = {answer.case_id: answer for answer in answers}
    observed = {prediction.case_id: prediction for prediction in predictions}
    cases = tuple(
        ReviewedCase(transcript, expected[transcript.case_id], observed[transcript.case_id])
        for transcript in dataset.transcripts
    )
    return SavedEvaluation(
        directory, report, system, dataset, cases, sha256(report_raw).hexdigest()
    )


def _validate_snapshot(
    directory: Path,
    declaration: EvaluationDeclaration,
    ready: InferenceComplete,
    system: dict[str, JsonValue],
    report: EvaluationReport,
    dataset: DatasetSplit,
    predictions_raw: bytes,
) -> None:
    identities = (
        directory.name == declaration.evaluation_id == ready.evaluation_id == report.evaluation_id,
        report.split == declaration.split == dataset.name == "development",
        declaration.dataset_version == report.dataset_version == dataset.version,
        declaration.dataset_manifest_sha256
        == report.dataset_manifest_sha256
        == dataset.manifest_sha256,
        declaration.inputs_sha256 == report.inputs_sha256 == dataset.inputs_sha256,
        report.answers_sha256 == dataset.answers_sha256,
        sha256(read_bounded(directory / "inputs.jsonl")).hexdigest() == dataset.inputs_sha256,
        ready.predictions_sha256
        == report.predictions_sha256
        == sha256(predictions_raw).hexdigest(),
        ready.system_sha256 == report.system_sha256 == digest_json(system),
        ready.count == report.score.total == len(dataset.transcripts),
        report.definitions == validate_contract(ScoreDefinitions, SCORE_DEFINITIONS),
    )
    if not all(identities):
        raise ValueError("Saved evaluation identities, coverage or artifact hashes differ.")


def _validate_run_configuration(
    directory: Path, predictions: tuple[Prediction, ...], system: SystemConfiguration
) -> None:
    for prediction in predictions:
        saved = validate_record(
            RUN_RECORD,
            parse_json(read_bounded(directory / "runs" / f"{prediction.run_id}.json").decode()),
        )
        provenance = saved.run.provenance
        fields = (
            "model_digest",
            "model_metadata_sha256",
            "runtime_url",
            "prompt_version",
            "prompt_sha256",
            "policy_version",
            "policy_sha256",
        )
        if (
            provenance.model != system.model
            or any(
                getattr(provenance, field) is not None
                and getattr(provenance, field) != getattr(system, field)
                for field in fields
            )
            or provenance.runtime_version not in {"unknown", system.runtime_version}
        ):
            raise ValueError("Saved case provenance differs from the evaluation configuration.")


def assert_baseline_compatible(baseline: SavedEvaluation, dataset: DatasetSplit) -> None:
    """Check the selected baseline before spending any new inference time."""
    report = baseline.report
    expected = {row.case_id: row.text_sha256 for row in dataset.transcripts}
    observed = {row.transcript.case_id: row.transcript.text_sha256 for row in baseline.cases}
    if (
        dataset.name != "development"
        or report.split != "development"
        or report.dataset_version != dataset.version
        or report.dataset_manifest_sha256 != dataset.manifest_sha256
        or report.inputs_sha256 != dataset.inputs_sha256
        or report.answers_sha256 != dataset.answers_sha256
        or expected != observed
    ):
        raise ValueError("Baseline requires the same development dataset, answers and exact cases.")
    if baseline.report.definitions != validate_contract(ScoreDefinitions, SCORE_DEFINITIONS):
        raise ValueError(
            "Baseline scorer or metric definitions differ; results are not comparable."
        )


def compare_reviews(current: SavedEvaluation, baseline: SavedEvaluation) -> Comparison:
    assert_baseline_compatible(baseline, current.dataset)
    if (
        current.report.score_version != baseline.report.score_version
        or current.report.definitions != baseline.report.definitions
    ):
        raise ValueError(
            "Baseline scorer or metric definitions differ; results are not comparable."
        )
    changes: list[MetricChange] = []
    for name in METRIC_LABELS:
        old: RatioRecord = getattr(baseline.report.score.metrics, name)
        new: RatioRecord = getattr(current.report.score.metrics, name)
        delta = None if old.value is None or new.value is None else (new.value - old.value) * 100
        changes.append(MetricChange(name, old, new, delta))
    prior = {row.transcript.case_id: row for row in baseline.cases}
    case_changes: list[CaseChange] = []
    for row in current.cases:
        old_case = prior[row.transcript.case_id]
        if old_case.prediction.result == row.prediction.result:
            continue
        kind = "fixed" if row.correct and not old_case.correct else "changed"
        if old_case.correct and not row.correct:
            kind = "regressed"
        case_changes.append(CaseChange(row.transcript.case_id, old_case, row, kind))
    old_unsafe = set(baseline.report.score.unsafe_misses)
    new_unsafe = set(current.report.score.unsafe_misses)
    old_config = baseline.system.model_dump(mode="json")
    new_config = current.system.model_dump(mode="json")
    return Comparison(
        baseline.report.evaluation_id,
        current.report.evaluation_id,
        tuple(changes),
        tuple(case_changes),
        tuple(change.case_id for change in case_changes if change.kind == "fixed"),
        tuple(change.case_id for change in case_changes if change.kind == "regressed"),
        tuple(sorted(new_unsafe - old_unsafe)),
        tuple(sorted(old_unsafe - new_unsafe)),
        tuple(key for key in new_config if new_config[key] != old_config[key]),
    )


def format_ratio(ratio: RatioRecord) -> str:
    suffix = "undefined" if ratio.value is None else f"{ratio.value:.1%}"
    return f"{ratio.numerator}/{ratio.denominator} ({suffix})"


def summary_text(current: SavedEvaluation, comparison: Comparison | None = None) -> str:
    report = current.report
    rows = [
        f"Evaluation {report.evaluation_id}",
        f"Development cases: {report.score.total}; correct: {report.score.correct_outputs}",
    ]
    rows.extend(
        f"{label}: {format_ratio(getattr(report.score.metrics, name))}"
        for name, label in METRIC_LABELS.items()
    )
    failures = sum(isinstance(row.prediction.result, Failure) for row in current.cases)
    rows.extend(
        [
            f"Unsafe misses: {len(report.score.unsafe_misses)}; processing failures: {failures}",
            "Quality acceptance: not established by this run.",
            current.verification,
        ]
    )
    if comparison is not None:
        rows.append(
            f"Baseline {comparison.baseline_id}: {len(comparison.fixes)} fixes; "
            f"{len(comparison.regressions)} regressions; {len(comparison.cases)} changed cases."
        )
        rows.append(
            f"New unsafe misses: {len(comparison.new_unsafe_misses)}; "
            f"removed unsafe misses: {len(comparison.removed_unsafe_misses)}"
        )
    return "\n".join(rows)


def render_review(current: SavedEvaluation, baseline: SavedEvaluation | None = None) -> Path:
    """Write an additive self-contained report; preserve earlier derived files."""
    from .evaluation_report import render_review_html

    comparison = compare_reviews(current, baseline) if baseline is not None else None
    html = render_review_html(current, baseline, comparison).encode("utf-8")
    if baseline is None:
        name = "review.html"
    else:
        # The report digest binds the projection to the exact chosen baseline.
        name = f"review-baseline-{baseline.report_sha256}.html"
    path = current.directory / name
    if path.exists() and read_bounded(path, 16 * 1024 * 1024) != html:
        # Preserve earlier projections and keep any selected baseline identity.
        path = path.with_name(f"{path.stem}-{sha256(html).hexdigest()[:16]}.html")
    try:
        with path.open("xb") as stream:
            stream.write(html)
    except FileExistsError:
        if read_bounded(path, 16 * 1024 * 1024) != html:
            raise ValueError(
                "Existing content-addressed review differs; preserve it and inspect the artifact."
            ) from None
    return path
