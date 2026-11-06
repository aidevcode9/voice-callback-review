"""Pure three-outcome scoring. Failures remain in coverage and callback recall."""

from dataclasses import dataclass

from .domain import CallbackDecision, Failure, JsonValue, Outcome


@dataclass(frozen=True)
class ReferenceAnswer:
    case_id: str
    label: Outcome
    rationale: str


@dataclass(frozen=True)
class Prediction:
    case_id: str
    transcript_sha256: str
    run_id: str
    result: CallbackDecision | Failure


@dataclass(frozen=True)
class Ratio:
    numerator: int
    denominator: int

    @property
    def value(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None

    def document(self) -> dict[str, JsonValue]:
        return {"numerator": self.numerator, "denominator": self.denominator, "value": self.value}


@dataclass(frozen=True)
class ScoreReport:
    total: int
    valid_outputs: int
    correct_outputs: int
    confusion_matrix: dict[str, dict[str, int]]
    processing_failures_by_expected: dict[str, int]
    failure_codes: dict[str, int]
    metrics: dict[str, dict[str, JsonValue]]
    unsafe_misses: tuple[str, ...]
    disagreements: tuple[dict[str, JsonValue], ...]


def score(predictions: tuple[Prediction, ...], answers: tuple[ReferenceAnswer, ...]) -> ScoreReport:
    expected = {answer.case_id: answer for answer in answers}
    observed = {prediction.case_id: prediction for prediction in predictions}
    if (
        len(expected) != len(answers)
        or len(observed) != len(predictions)
        or set(expected) != set(observed)
    ):
        raise ValueError(
            "Scoring requires unique, exact case coverage; missing or foreign cases are invalid."
        )
    matrix = {label.value: {other.value: 0 for other in Outcome} for label in Outcome}
    failures = {label.value: 0 for label in Outcome}
    failure_codes: dict[str, int] = {}
    unsafe: list[str] = []
    disagreements: list[dict[str, JsonValue]] = []
    valid = correct = predicted_callbacks = predicted_review = true_callbacks = (
        expected_callbacks
    ) = 0
    for answer in answers:
        prediction = observed[answer.case_id]
        result = prediction.result
        expected_callbacks += answer.label == Outcome.CALLBACK_REQUIRED
        detail: dict[str, JsonValue] = {
            "case_id": answer.case_id,
            "expected_label": answer.label.value,
            "reference_rationale": answer.rationale,
            "run_id": prediction.run_id,
        }
        if isinstance(result, Failure):
            failures[answer.label.value] += 1
            failure_codes[result.code.value] = failure_codes.get(result.code.value, 0) + 1
            detail.update(
                {
                    "predicted_label": None,
                    "failure_code": result.code.value,
                    "failure_message": result.message,
                }
            )
        else:
            valid += 1
            matrix[answer.label.value][result.label.value] += 1
            correct += answer.label == result.label
            predicted_callbacks += result.label == Outcome.CALLBACK_REQUIRED
            predicted_review += result.label == Outcome.NEEDS_REVIEW
            true_callbacks += answer.label == result.label == Outcome.CALLBACK_REQUIRED
            if answer.label == Outcome.CALLBACK_REQUIRED and result.label == Outcome.NO_CALLBACK:
                unsafe.append(answer.case_id)
            if answer.label == result.label:
                continue
            detail.update(
                {
                    "predicted_label": result.label.value,
                    "reason": result.reason,
                    "evidence": list(result.evidence),
                }
            )
        disagreements.append(detail)
    total = len(answers)
    return ScoreReport(
        total,
        valid,
        correct,
        matrix,
        failures,
        failure_codes,
        {
            "strict_callback_recall": Ratio(true_callbacks, expected_callbacks).document(),
            "callback_precision": Ratio(true_callbacks, predicted_callbacks).document(),
            "needs_review_rate": Ratio(predicted_review, total).document(),
            "valid_output_coverage": Ratio(valid, total).document(),
        },
        tuple(unsafe),
        tuple(disagreements),
    )
