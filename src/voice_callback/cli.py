"""Local runtime diagnostics and explicit text classification with JSON run records."""

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from .classify import classify, load_transcript
from .domain import JsonValue, ModelConfig, RunSuccess, Stage
from .evaluate import evaluate, freeze_run, read_document, score_run
from .models import list_models, load_registry
from .ollama import OllamaClient, OllamaError, doctor
from .storage import render_run, save_run


def _classify_command(
    args: argparse.Namespace, client: OllamaClient, configs: tuple[ModelConfig, ...]
) -> int:
    matches = [config for config in configs if config.id == args.model]
    if len(matches) != 1:
        raise ValueError("Choose a model configuration ID listed by models --stage classification.")
    transcript = load_transcript(args.input, args.case_id, args.transcript_version)
    result = classify(transcript, matches[0], client, policy_path=args.policy)
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


def _print_evaluation(report: dict[str, JsonValue], directory: Path) -> int:
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
    directory = evaluate(
        args.dataset,
        args.split,
        matches[0],
        client,
        output_root=args.output_dir,
        policy_path=args.policy,
        frozen_path=args.frozen_config,
        allow_held_out=args.allow_held_out,
    )
    return _print_evaluation(read_document(directory / "report.json"), directory)


def _artifact_command(args: argparse.Namespace) -> int:
    if args.command == "score":
        return _print_evaluation(score_run(args.run_dir, args.dataset), args.run_dir)
    path = freeze_run(args.run_dir, args.dataset, args.output)
    print(json.dumps({"status": "frozen", "configuration_path": str(path)}))
    return 0


def main(argv: list[str] | None = None) -> int:
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
            command.add_argument("--split", required=True, choices=("development", "evaluation"))
            command.add_argument("--output-dir", type=Path, default=Path("reports/text"))
            command.add_argument("--frozen-config", type=Path)
            command.add_argument("--allow-held-out", action="store_true")
    for name in ("score", "freeze-evaluation"):
        command = subparsers.add_parser(name)
        command.add_argument("--run-dir", required=True, type=Path)
        command.add_argument("--dataset", type=Path, default=Path("data/gold/v1.0"))
        if name == "freeze-evaluation":
            command.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in {"score", "freeze-evaluation"}:
            return _artifact_command(args)
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
    except ValueError as error:
        print(json.dumps({"status": "configuration_error", "message": str(error)}))
        return 2
    except OllamaError as error:
        print(json.dumps({"status": "processing_error", "failure": asdict(error.failure)}))
        return 1
    except OSError:
        print(
            json.dumps(
                {
                    "status": "io_error",
                    "message": "Cannot read or write operation artifacts; check paths and permissions.",
                }
            )
        )
        return 1
    except KeyboardInterrupt:
        print(
            json.dumps(
                {
                    "status": "interrupted",
                    "message": "Evaluation interrupted; incomplete artifacts are retained and cannot be scored.",
                }
            )
        )
        return 130
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
