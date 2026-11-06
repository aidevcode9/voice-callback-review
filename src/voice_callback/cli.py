"""JSON diagnostics. Zero installed models is a successful observation, not inference."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import shutil

from .domain import Stage
from .models import list_models, load_registry
from .ollama import OllamaClient, doctor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "models"):
        command = subparsers.add_parser(name)
        command.add_argument("--url", default="http://127.0.0.1:11434")
        command.add_argument("--timeout", type=float, default=3.0)
        command.add_argument("--registry", type=Path, default=Path("config/models.json"))
        if name == "models":
            command.add_argument("--stage", choices=[stage.value for stage in Stage])
    args = parser.parse_args(argv)
    try:
        client = OllamaClient(args.url, timeout=args.timeout)
        configs = load_registry(args.registry)
    except ValueError as error:
        print(json.dumps({"status": "configuration_error", "message": str(error)}))
        return 2
    report = doctor(client)
    stage = Stage(args.stage) if args.command == "models" and args.stage else None
    choices = list_models(configs, report.installed_models, stage)
    installed = report.installed_models
    messages = ["Inference was not run. Configured capabilities do not establish model quality."]
    if installed == ():
        messages.append("Ollama is reachable with zero installed models. Choose a classifier before explicit provisioning in batch 2.")
    if not any(Stage.CLASSIFICATION in config.stages for config in configs):
        messages.append("No classifier is configured; owner selection remains deferred.")
    if not any(choice.selectable for choice in choices):
        messages.append("No installed compatible choices are available for this selection.")
    binary = shutil.which("ollama")
    if binary is None:
        messages.append("Ollama executable was not found on PATH; server availability is checked independently.")
    result = {
        "status": "diagnostic_error" if report.failures else "ok",
        "ollama_binary": binary,
        "server_version": report.version,
        "installed_models": None if installed is None else [asdict(model) for model in installed],
        "configured_models": [
            {"id": choice.config.id, "runtime": choice.config.runtime.value,
             "model_id": choice.config.model_id, "stages": [s.value for s in choice.config.stages],
             "settings": dict(choice.config.settings), "availability": choice.status,
             "digest": choice.digest, "selectable": choice.selectable}
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
