"""Persist input-only inference before opening answers for deterministic scoring."""

import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from .classify import classify, validate_decision
from .datasets import DatasetSplit, load_answers, load_split, object_value, string_value
from .domain import (
    CallbackDecision,
    Failure,
    FailureCode,
    JsonValue,
    ModelConfig,
    RunResult,
    RunSuccess,
)
from .evaluation_config import (
    digest_json,
    prepare_system,
    source_identity,
    verify_frozen,
    verify_run_system,
)
from .json_io import parse_json, parse_jsonl, read_bounded
from .ollama import OllamaClient
from .scoring import Prediction, score
from .storage import render_json, save_run, write_json


def read_document(path: Path) -> dict[str, JsonValue]:
    return object_value(parse_json(read_bounded(path).decode("utf-8")))


def _write_or_verify(path: Path, value: object) -> None:
    content = render_json(value).encode("utf-8")
    if path.exists():
        if read_bounded(path) != content:
            raise ValueError(
                "Existing artifact differs; preserve it and use a new run or output path."
            )
        return
    write_json(path, value)


def _prediction_document(result: RunResult, run_path: Path) -> dict[str, JsonValue]:
    provenance = result.provenance
    document: dict[str, JsonValue] = {
        "case_id": provenance.case_id,
        "transcript_sha256": provenance.transcript_sha256,
        "run_id": provenance.run_id,
        "run_sha256": sha256(read_bounded(run_path)).hexdigest(),
    }
    if isinstance(result, RunSuccess):
        if not isinstance(result.output, CallbackDecision):
            raise ValueError("Evaluation requires a classification result.")
        document.update(
            {"status": "success", "output": object_value(parse_json(render_json(result.output)))}
        )
    else:
        document.update(
            {
                "status": "processing_error",
                "failure": object_value(parse_json(render_json(result.failure))),
            }
        )
    return document


def _read_predictions(raw: bytes, dataset: DatasetSplit, directory: Path) -> tuple[Prediction, ...]:
    transcripts = {row.case_id: row for row in dataset.transcripts}
    predictions: list[Prediction] = []
    ids: set[str] = set()
    runs: set[str] = set()
    for value in parse_jsonl(raw):
        row = object_value(value)
        status = row.get("status")
        field = "output" if status == "success" else "failure"
        if (
            not isinstance(status, str)
            or set(row)
            != {
                "case_id",
                "transcript_sha256",
                "run_id",
                "run_sha256",
                "status",
                field,
            }
            or status not in {"success", "processing_error"}
        ):
            raise ValueError("Prediction schema is invalid.")
        case_id, run_id = string_value(row["case_id"]), string_value(row["run_id"])
        if (
            case_id not in transcripts
            or case_id in ids
            or run_id in runs
            or str(UUID(run_id)) != run_id
        ):
            raise ValueError("Predictions require unique known cases and canonical run IDs.")
        ids.add(case_id)
        runs.add(run_id)
        transcript = transcripts[case_id]
        if row["transcript_sha256"] != transcript.text_sha256:
            raise ValueError("Prediction is bound to a different transcript.")
        run_bytes = read_bounded(directory / "runs" / f"{run_id}.json")
        run_record = object_value(parse_json(run_bytes.decode("utf-8")))
        run = object_value(run_record.get("run"))
        provenance = object_value(run.get("provenance"))
        if (
            sha256(run_bytes).hexdigest() != row["run_sha256"]
            or run_record.get("status") != status
            or provenance.get("case_id") != case_id
            or provenance.get("run_id") != run_id
            or provenance.get("transcript_sha256") != transcript.text_sha256
            or run.get(field) != row[field]
        ):
            raise ValueError("Saved run provenance or prediction integrity differs.")
        if status == "success":
            result: CallbackDecision | Failure = validate_decision(
                json.dumps(row[field]), transcript.text
            )
        else:
            failure = object_value(row[field])
            if set(failure) != {"code", "message"}:
                raise ValueError("Processing failure schema is invalid.")
            message = string_value(failure["message"])
            if len(message) > 1200:
                raise ValueError("Processing failure message exceeds its limit.")
            result = Failure(FailureCode(failure["code"]), message)
        predictions.append(Prediction(case_id, transcript.text_sha256, run_id, result))
    if ids != set(transcripts):
        raise ValueError("Incomplete predictions cannot be scored.")
    return tuple(predictions)


def score_run(directory: Path, dataset_root: Path) -> dict[str, JsonValue]:
    job = read_document(directory / "evaluation.json")
    ready = read_document(directory / "inference-complete.json")
    system = read_document(directory / "configuration.json")
    if (
        job.get("schema_version") != 1
        or ready.get("schema_version") != 1
        or (directory / "aborted.json").exists()
    ):
        raise ValueError("Only completed inference can be scored.")
    split = string_value(job.get("split"))
    dataset = load_split(dataset_root, split)
    inputs = read_bounded(directory / "inputs.jsonl")
    predictions_raw = read_bounded(directory / "predictions.jsonl", 16 * 1024 * 1024)
    if (
        job.get("evaluation_id") != ready.get("evaluation_id")
        or job.get("dataset_manifest_sha256") != dataset.manifest_sha256
        or job.get("dataset_version") != dataset.version
        or job.get("inputs_sha256") != dataset.inputs_sha256
        or sha256(inputs).hexdigest() != dataset.inputs_sha256
        or ready.get("predictions_sha256") != sha256(predictions_raw).hexdigest()
        or ready.get("system_sha256") != digest_json(system)
        or ready.get("count") != len(dataset.transcripts)
        or object_value(system.get("code")).get("source_sha256")
        != source_identity()["source_sha256"]
    ):
        raise ValueError("Evaluation artifact, dataset, or scoring-code identity differs.")
    predictions = _read_predictions(predictions_raw, dataset, directory)
    answers = load_answers(dataset)
    scored = score(predictions, answers)
    report: dict[str, JsonValue] = {
        "schema_version": 1,
        "evaluation_id": job["evaluation_id"],
        "split": split,
        "dataset_version": dataset.version,
        "dataset_manifest_sha256": dataset.manifest_sha256,
        "inputs_sha256": dataset.inputs_sha256,
        "answers_sha256": dataset.answers_sha256,
        "predictions_sha256": ready["predictions_sha256"],
        "system_sha256": digest_json(system),
        "trial_count": 1,
        "score_version": "callback-score-v1",
        "score": object_value(parse_json(render_json(scored))),
        "definitions": {
            "confusion_matrix": "Rows are expected outcomes; columns are valid predicted outcomes. Processing failures are separate.",
            "strict_callback_recall": "Correct callback predictions / all expected callbacks, including failures and needs_review.",
            "callback_precision": "Correct callback predictions / valid predicted callbacks.",
            "needs_review_rate": "Valid needs_review outputs / all input cases, including failures.",
            "valid_output_coverage": "Validated outputs / all input cases.",
            "undefined": "A zero denominator has value null.",
        },
        "limitations": [
            "One trial on a small fictional grouped split.",
            "No repeatability spread, model comparison, performance claim, or quality threshold is established.",
        ],
    }
    _write_or_verify(directory / "report.json", report)
    return report


def evaluate(
    dataset_root: Path,
    split: str,
    model: ModelConfig,
    client: OllamaClient,
    *,
    output_root: Path = Path("reports/text"),
    policy_path: Path = Path("docs/CALLBACK_POLICY.md"),
    frozen_path: Path | None = None,
    allow_held_out: bool = False,
) -> Path:
    if split == "evaluation" and (not allow_held_out or frozen_path is None):
        raise ValueError(
            "Held-out inference requires --allow-held-out and --frozen-config explicitly."
        )
    if split == "development" and (allow_held_out or frozen_path is not None):
        raise ValueError(
            "Frozen configuration and held-out opt-in apply only to the evaluation split."
        )
    dataset = load_split(dataset_root, split)
    system = prepare_system(dataset, model, client, policy_path)
    if frozen_path is not None:
        verify_frozen(read_document(frozen_path), system, dataset)
    evaluation_id = str(uuid4())
    directory = output_root / evaluation_id
    directory.mkdir(parents=True)
    completed = 0
    try:
        write_json(directory / "configuration.json", system)
        write_json(
            directory / "evaluation.json",
            {
                "schema_version": 1,
                "evaluation_id": evaluation_id,
                "split": split,
                "dataset_version": dataset.version,
                "dataset_manifest_sha256": dataset.manifest_sha256,
                "inputs_sha256": dataset.inputs_sha256,
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        with (directory / "inputs.jsonl").open("xb") as stream:
            stream.write(dataset.input_bytes)
        with (directory / "predictions.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
            for transcript in dataset.transcripts:
                result = classify(transcript, model, client, policy_path=policy_path)
                path = save_run(result, directory / "runs")
                if (
                    result.provenance.case_id != transcript.case_id
                    or result.provenance.transcript_sha256 != transcript.text_sha256
                ):
                    raise ValueError("Classification result is bound to another input.")
                verify_run_system(result, system)
                stream.write(
                    json.dumps(
                        _prediction_document(result, path), ensure_ascii=True, allow_nan=False
                    )
                    + "\n"
                )
                stream.flush()
                completed += 1
        if (
            source_identity() != system["code"]
            or sha256(read_bounded(policy_path)).hexdigest() != system["policy_sha256"]
        ):
            raise ValueError("System changed before inference completed; results remain unscored.")
        write_json(
            directory / "inference-complete.json",
            {
                "schema_version": 1,
                "evaluation_id": evaluation_id,
                "count": completed,
                "system_sha256": digest_json(system),
                "predictions_sha256": sha256(
                    read_bounded(directory / "predictions.jsonl", 16 * 1024 * 1024)
                ).hexdigest(),
            },
        )
    except BaseException:
        try:
            write_json(
                directory / "aborted.json",
                {"status": "incomplete", "completed_predictions": completed},
            )
        except OSError:
            pass
        raise
    score_run(directory, dataset_root)
    return directory


def freeze_run(directory: Path, dataset_root: Path, output: Path | None = None) -> Path:
    report = score_run(directory, dataset_root)
    scored = object_value(report["score"])
    system = read_document(directory / "configuration.json")
    current = source_identity()
    original = object_value(system.get("code"))
    if (
        report["split"] != "development"
        or scored["valid_outputs"] != scored["total"]
        or current["working_tree_clean"] is not True
        or original.get("working_tree_clean") is not True
        or current["git_revision"] is None
        or current["source_sha256"] != original.get("source_sha256")
    ):
        raise ValueError(
            "Freeze requires a complete development baseline without processing failures and unchanged clean committed source."
        )
    path = output if output is not None else directory / "frozen-configuration.json"
    _write_or_verify(
        path,
        {
            "schema_version": 1,
            "kind": "frozen_callback_system",
            "system": system,
            "system_sha256": digest_json(system),
            "dataset_manifest_sha256": report["dataset_manifest_sha256"],
            "development_evaluation_id": report["evaluation_id"],
            "development_report_sha256": sha256(
                read_bounded(directory / "report.json")
            ).hexdigest(),
            "frozen_revision": current["git_revision"],
        },
    )
    return path
