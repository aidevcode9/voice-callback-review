"""Optional Langfuse observations for local inference."""

import importlib
import logging
import os
from dataclasses import dataclass
from typing import Any

from .domain import CallbackDecision, JsonValue, RunFailure, RunResult, RunSuccess

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluationTraceContext:
    evaluation_id: str
    split: str
    dataset_version: str
    case_id: str


def _get_client() -> Any:
    return importlib.import_module("langfuse").get_client()


class ClassificationTrace:
    def __init__(self, model: str, run_id: str, evaluation: EvaluationTraceContext | None = None):
        self.client: Any = None
        self.root: Any = None
        self.generation: Any = None
        self.include_content = os.environ.get("VCR_LANGFUSE_CONTENT", "1") == "1"
        if os.environ.get("VCR_LANGFUSE_ENABLED") != "1":
            return
        if not all(
            os.environ.get(key)
            for key in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
        ):
            logger.warning("Langfuse tracing is enabled but configuration is incomplete.")
            return
        try:
            self.client = _get_client()
            metadata = {"run_id": run_id}
            if evaluation is not None:
                metadata.update(
                    evaluation_id=evaluation.evaluation_id,
                    split=evaluation.split,
                    dataset_version=evaluation.dataset_version,
                    case_id=evaluation.case_id,
                )
            self.root = self.client.start_observation(
                name="callback-classification",
                as_type="span",
                input={"stage": "classification"},
                metadata=metadata,
            )
        except Exception:
            logger.warning("Langfuse tracing could not be initialized.")

    def begin_generation(self, model: str, transcript: str) -> None:
        if self.root is None:
            return
        try:
            trace_input = (
                {"transcript": transcript} if self.include_content else {"content": "omitted"}
            )
            self.root.update(input=trace_input)
            self.generation = self.root.start_observation(
                name="ollama-classification",
                as_type="generation",
                model=model,
                input=trace_input,
            )
        except Exception:
            logger.warning("Langfuse generation could not be initialized.")

    def generated(self, response: dict[str, JsonValue]) -> None:
        if self.generation is None:
            return
        usage: dict[str, int] = {}
        for source, target in (("prompt_eval_count", "input"), ("eval_count", "output")):
            count = response.get(source)
            if type(count) is int and count >= 0:
                usage[target] = count
        try:
            self.generation.update(usage_details=usage)
        except Exception:
            logger.warning("Langfuse generation update failed.")

    def finish(self, result: RunResult) -> None:
        try:
            output: dict[str, Any] = {"status": "failure"}
            if isinstance(result, RunSuccess):
                output = {"status": "success"}
                if self.include_content and isinstance(result.output, CallbackDecision):
                    output.update(
                        label=result.output.label.value,
                        rule_ids=list(result.output.rule_ids),
                        reason=result.output.reason,
                        evidence=list(result.output.evidence),
                    )
            if self.generation is not None:
                if isinstance(result, RunFailure):
                    self.generation.update(level="ERROR", status_message=result.failure.code.value)
                self.generation.update(output=output)
                self.generation.end()
            if self.root is not None:
                if isinstance(result, RunFailure):
                    self.root.update(level="ERROR", status_message=result.failure.code.value)
                self.root.update(output=output)
                self.root.end()
            if self.client is not None:
                self.client.flush()
        except Exception:
            logger.warning("Langfuse trace could not be completed.")
