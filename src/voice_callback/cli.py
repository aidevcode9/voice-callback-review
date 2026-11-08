"""Local runtime diagnostics and explicit text classification with JSON run records."""

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from pydantic import TypeAdapter

from .admission import InferenceAdmission
from .classify import classify, load_transcript
from .datasets import load_split
from .domain import JsonValue, ModelConfig, RunSuccess, Stage
from .evaluate import EvaluationProgress, evaluate, freeze_run, read_document, score_run
from .evaluation_contracts import EvaluationDeclaration, EvaluationReport
from .evaluation_review import Comparison
from .models import list_models, load_registry
from .ollama import OllamaClient, OllamaError, doctor
from .storage import render_run, save_run
from .workspace import WorkspaceError


def _classify_command(
    args: argparse.Namespace, client: OllamaClient, configs: tuple[ModelConfig, ...]
) -> int:
    matches = [config for config in configs if config.id == args.model]
    if len(matches) != 1:
        raise ValueError("Choose a model configuration ID listed by models --stage classification.")
    transcript = load_transcript(args.input, args.case_id, args.transcript_version)
    with InferenceAdmission(args.inference_lock_dir).operation() as lease:
        result = classify(transcript, matches[0], client, policy_path=args.policy)
        lease.observe(result)
    try:
        path = save_run(result, args.output_dir)
    except OSError:
        print(
            json.dumps(
                {
                    "status": "storage_error",
                    "message": "Cannot save the run record; check the output directory.",
                    "run_id": result.provenance.run_id,
                }
            )
        )
        return 1
    print(render_run(result), end="")
    print(f"Run record: {path}", file=sys.stderr)
    return 0 if isinstance(result, RunSuccess) else 1


def _print_evaluation(
    report: dict[str, JsonValue],
    directory: Path,
    *,
    review_path: Path | None = None,
    comparison: Comparison | None = None,
) -> int:
    scored = report["score"]
    if not isinstance(scored, dict):
        raise ValueError("Evaluation report is invalid.")
    failed = scored["valid_outputs"] != scored["total"]
    print(
        json.dumps(
            {
                "status": "completed_with_failures" if failed else "completed",
                "report_path": str(directory / "report.json"),
                "report": report,
                "review_path": str(review_path) if review_path is not None else None,
                "comparison": TypeAdapter(Comparison).dump_python(comparison, mode="json")
                if comparison is not None
                else None,
            },
            indent=2,
        )
    )
    return 1 if failed else 0


def _evaluation_command(
    args: argparse.Namespace, client: OllamaClient, configs: tuple[ModelConfig, ...]
) -> int:
    matches = [config for config in configs if config.id == args.model]
    if len(matches) != 1:
        raise ValueError("Choose an explicit configured classifier ID.")
    baseline = None
    if args.baseline is not None:
        from .evaluation_review import assert_baseline_compatible, load_review

        baseline = load_review(args.baseline, args.dataset)
        assert_baseline_compatible(baseline, load_split(args.dataset, args.split))

    def progress(event: EvaluationProgress) -> None:
        if event.phase == "starting":
            print(f"Evaluation: {event.directory}", file=sys.stderr, flush=True)
        elif event.phase == "persisted":
            print(
                f"{event.completed}/{event.total} saved: {event.case_id}",
                file=sys.stderr,
                flush=True,
            )
        elif event.phase == "incomplete":
            print(
                f"Incomplete run preserved: {event.directory}. If provider completion is unknown, "
                "stop/restart Ollama, then use recover-inference --runtime-stopped before retrying.",
                file=sys.stderr,
                flush=True,
            )
        else:
            print(f"Evaluation {event.phase}.", file=sys.stderr, flush=True)

    with InferenceAdmission(args.inference_lock_dir).operation() as lease:
        directory = evaluate(
            args.dataset,
            args.split,
            matches[0],
            client,
            output_root=args.output_dir,
            policy_path=args.policy,
            frozen_path=args.frozen_config,
            allow_held_out=args.allow_held_out,
            observe_result=lease.observe,
            progress=progress,
        )
    if args.split == "development":
        from .evaluation_review import compare_reviews, load_review, render_review, summary_text

        current = load_review(directory, args.dataset)
        comparison = compare_reviews(current, baseline) if baseline is not None else None
        review_path = render_review(current, baseline)
        if not args.json:
            print(summary_text(current, comparison))
            print(f"Browser report: {review_path}")
            return 0 if current.report.score.valid_outputs == current.report.score.total else 1
        return _print_evaluation(
            read_document(directory / "report.json", EvaluationReport),
            directory,
            review_path=review_path,
            comparison=comparison,
        )
    return _print_evaluation(read_document(directory / "report.json", EvaluationReport), directory)


def _artifact_command(args: argparse.Namespace) -> int:
    if args.command == "score":
        return _print_evaluation(score_run(args.run_dir, args.dataset), args.run_dir)
    path = freeze_run(args.run_dir, args.dataset, args.output)
    print(json.dumps({"status": "frozen", "configuration_path": str(path)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "models", "classify", "evaluate"):
        command = subparsers.add_parser(name)
        command.add_argument("--url", default="http://127.0.0.1:11434")
        command.add_argument("--timeout", type=float, default=3.0)
        command.add_argument("--registry", type=Path, default=Path("config/models.json"))
        if name == "models":
            command.add_argument("--stage", choices=[stage.value for stage in Stage])
        if name in {"classify", "evaluate"}:
            command.add_argument(
                "--inference-lock-dir", type=Path, default=Path("runtime/inference")
            )
            command.add_argument(
                "--model", required=True, help="Explicit configuration ID; no default."
            )
            command.add_argument("--policy", type=Path, default=Path("docs/CALLBACK_POLICY.md"))
            command.add_argument("--inference-timeout", type=float, default=180.0)
        if name == "classify":
            command.add_argument("--input", required=True, type=Path)
            command.add_argument("--case-id", required=True)
            command.add_argument("--transcript-version")
            command.add_argument("--output-dir", type=Path, default=Path("runtime/classifications"))
        if name == "evaluate":
            command.add_argument("--dataset", type=Path, default=Path("data/gold/v1.0"))
            command.add_argument(
                "--split", default="development", choices=("development", "evaluation")
            )
            command.add_argument("--output-dir", type=Path, default=Path("reports/text"))
            command.add_argument("--frozen-config", type=Path)
            command.add_argument("--allow-held-out", action="store_true")
            command.add_argument(
                "--baseline", type=Path, help="Compare a completed development run."
            )
            command.add_argument(
                "--json", action="store_true", help="Print machine-readable results."
            )
            command.add_argument("--trace", action=argparse.BooleanOptionalAction, default=None)
            command.add_argument("--metadata-only", action="store_true")
            command.add_argument(
                "--prepare-only", action="store_true", help="Prepare without inference."
            )
    review = subparsers.add_parser(
        "evaluations", help="List or review saved development evaluations."
    )
    review.add_argument("--run-dir", type=Path)
    review.add_argument("--baseline", type=Path)
    review.add_argument("--dataset", type=Path, default=Path("data/gold/v1.0"))
    review.add_argument("--output-dir", type=Path, default=Path("reports/text"))
    review.add_argument("--json", action="store_true")
    for name in ("score", "freeze-evaluation"):
        command = subparsers.add_parser(name)
        command.add_argument("--run-dir", required=True, type=Path)
        command.add_argument("--dataset", type=Path, default=Path("data/gold/v1.0"))
        if name == "freeze-evaluation":
            command.add_argument("--output", type=Path)
    recover = subparsers.add_parser("recover-inference")
    recover.add_argument(
        "--runtime-stopped",
        action="store_true",
        required=True,
        help="Confirm you stopped/restarted Ollama after an interrupted operation.",
    )
    recover.add_argument("--inference-lock-dir", type=Path, default=Path("runtime/inference"))
    return parser


def _saved_evaluations(args: argparse.Namespace) -> int:
    from .evaluation_review import compare_reviews, load_review, render_review, summary_text

    if args.run_dir is not None:
        current = load_review(args.run_dir, args.dataset)
        baseline = load_review(args.baseline, args.dataset) if args.baseline is not None else None
        comparison = compare_reviews(current, baseline) if baseline is not None else None
        path = render_review(current, baseline)
        if args.json:
            return _print_evaluation(
                read_document(args.run_dir / "report.json", EvaluationReport),
                args.run_dir,
                review_path=path,
                comparison=comparison,
            )
        print(summary_text(current, comparison))
        print(f"Browser report: {path}")
        return 0
    if args.baseline is not None:
        raise ValueError("Choose --run-dir when comparing a saved baseline.")
    rows: list[dict[str, JsonValue]] = []
    for path in sorted(args.output_dir.glob("*/evaluation.json")):
        started_at: JsonValue = None
        try:
            declaration = read_document(path, EvaluationDeclaration)
            if declaration["split"] != "development":
                continue
            started_at = declaration["started_at"]
            status = "incomplete"
            if (path.parent / "report.json").is_file() and not (
                path.parent / "aborted.json"
            ).exists():
                load_review(path.parent, args.dataset)
                status = "completed"
        except (ValueError, OSError):
            status = "invalid"
        rows.append({"run_dir": str(path.parent), "status": status, "started_at": started_at})
    rows.sort(key=lambda row: str(row["started_at"] or ""), reverse=True)
    if args.json:
        print(json.dumps({"evaluations": rows}, indent=2))
    else:
        print("Saved development evaluations (no inference):")
        for row in rows:
            print(f"{row['started_at'] or 'unknown date'} / {row['status']}: {row['run_dir']}")
        if not rows:
            print("No saved development evaluations. Start with evaluate --model MODEL_ID.")
    return 0


def _development_command(args: argparse.Namespace) -> int:
    from .evaluation_workflow import DevelopmentRequest, repository_root, run_development

    status = InferenceAdmission(args.inference_lock_dir).status()
    if status == "busy":
        raise WorkspaceError("job_busy", 409, "Another local inference operation is active.")
    if status == "recovery_required":
        raise WorkspaceError(
            "recovery_required",
            503,
            "Stop/restart Ollama and explicitly recover admission before another evaluation.",
        )
    return run_development(
        DevelopmentRequest(
            repository=repository_root(),
            model_id=args.model,
            dataset=args.dataset.resolve(),
            registry=args.registry.resolve(),
            policy=args.policy.resolve(),
            output=args.output_dir.resolve(),
            inference_lock=args.inference_lock_dir.resolve(),
            baseline=args.baseline.resolve() if args.baseline is not None else None,
            tracing=args.trace,
            metadata_only=args.metadata_only,
            prepare_only=args.prepare_only,
            json_output=args.json,
            url=args.url,
            timeout=args.timeout,
            inference_timeout=args.inference_timeout,
        )
    )


def operation_error(
    error: WorkspaceError | ValueError | OllamaError | OSError | KeyboardInterrupt,
) -> int:
    if isinstance(error, WorkspaceError):
        result = {
            "status": "processing_error",
            "failure": {"code": error.code, "message": error.message},
        }
        code = 1
    elif isinstance(error, ValueError):
        result = {"status": "configuration_error", "message": str(error)}
        code = 2
    elif isinstance(error, OllamaError):
        result = {"status": "processing_error", "failure": asdict(error.failure)}
        code = 1
    elif isinstance(error, KeyboardInterrupt):
        result = {
            "status": "interrupted",
            "message": "Evaluation interrupted; incomplete artifacts are retained and cannot be scored.",
        }
        code = 130
    else:
        result = {
            "status": "io_error",
            "message": "Cannot read or write operation artifacts; check paths and permissions.",
        }
        code = 1
    print(json.dumps(result))
    return code


def execute_development(args: argparse.Namespace) -> int:
    client = OllamaClient(args.url, timeout=args.timeout, inference_timeout=args.inference_timeout)
    return _evaluation_command(args, client, load_registry(args.registry))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "recover-inference":
            InferenceAdmission(args.inference_lock_dir).recover()
            print(
                json.dumps(
                    {"status": "recovered", "message": "Local inference admission recovered."}
                )
            )
            return 0
        if args.command in {"score", "freeze-evaluation"}:
            return _artifact_command(args)
        if args.command == "evaluations":
            return _saved_evaluations(args)
        if args.command == "evaluate" and args.split == "development":
            if args.allow_held_out or args.frozen_config is not None:
                raise ValueError("Held-out options apply only to --split evaluation.")
            return _development_command(args)
        if args.command == "evaluate" and (
            args.baseline is not None
            or args.prepare_only
            or args.trace is not None
            or args.metadata_only
        ):
            raise ValueError("Development workflow options do not apply to held-out evaluation.")
        client = OllamaClient(
            args.url,
            timeout=args.timeout,
            inference_timeout=args.inference_timeout
            if args.command in {"classify", "evaluate"}
            else 180.0,
        )
        configs = load_registry(args.registry)
        if args.command == "classify":
            return _classify_command(args, client, configs)
        if args.command == "evaluate":
            return _evaluation_command(args, client, configs)
    except (WorkspaceError, ValueError, OllamaError, OSError, KeyboardInterrupt) as error:
        return operation_error(error)
    report = doctor(client)
    stage = Stage(args.stage) if args.command == "models" and args.stage else None
    choices = list_models(configs, report.installed_models, stage)
    installed = report.installed_models
    messages = ["Inference was not run. Configured capabilities do not establish model quality."]
    if installed == ():
        messages.append(
            "Ollama is reachable with zero installed models. Choose a classifier before explicit provisioning in batch 2."
        )
    if not any(Stage.CLASSIFICATION in config.stages for config in configs):
        messages.append("No classifier is configured; owner selection remains deferred.")
    if not any(choice.selectable for choice in choices):
        messages.append("No installed compatible choices are available for this selection.")
    binary = shutil.which("ollama")
    if binary is None:
        messages.append(
            "Ollama executable was not found on PATH; server availability is checked independently."
        )
    result = {
        "status": "diagnostic_error" if report.failures else "ok",
        "ollama_binary": binary,
        "server_version": report.version,
        "installed_models": None if installed is None else [asdict(model) for model in installed],
        "configured_models": [
            {
                "id": choice.config.id,
                "runtime": choice.config.runtime.value,
                "model_id": choice.config.model_id,
                "stages": [s.value for s in choice.config.stages],
                "settings": dict(choice.config.settings),
                "availability": choice.status,
                "digest": choice.digest,
                "selectable": choice.selectable,
            }
            for choice in choices
        ],
        "inference_verified": False,
        "failures": [asdict(failure) for failure in report.failures],
        "messages": messages,
    }
    print(json.dumps(result, indent=2))
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
