"""Private process boundary for executing prepared source, never another launcher."""

import sys

from .cli import build_parser, execute_artifact, execute_evaluation, operation_error
from .ollama import OllamaError
from .workspace import WorkspaceError


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"score", "freeze-evaluation"}:
            return execute_artifact(args)
        if args.command != "evaluate":
            parser.error("The evaluation worker accepts only evaluation and artifact operations.")
        if args.prepare_only or args.trace is not None or args.metadata_only:
            parser.error(
                "Preparation and tracing options belong to the parent evaluation workflow."
            )
        if args.split == "development" and (args.allow_held_out or args.frozen_config is not None):
            parser.error("Held-out options do not apply to development evaluation.")
        if args.split == "evaluation" and (not args.allow_held_out or args.frozen_config is None):
            parser.error("Held-out evaluation requires a frozen configuration and explicit opt-in.")
        return execute_evaluation(args)
    except (WorkspaceError, ValueError, OllamaError, OSError, KeyboardInterrupt) as error:
        return operation_error(error)


if __name__ == "__main__":
    sys.exit(main())
