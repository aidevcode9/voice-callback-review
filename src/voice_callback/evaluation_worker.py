"""Private process boundary for executing prepared source, never another launcher."""

import sys

from .cli import build_parser, execute_development, operation_error
from .ollama import OllamaError
from .workspace import WorkspaceError


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "evaluate" or args.split != "development":
        parser.error("The development worker accepts only development evaluation.")
    if args.allow_held_out or args.frozen_config is not None:
        parser.error("Held-out options are unavailable in the development worker.")
    if args.prepare_only or args.trace is not None or args.metadata_only:
        parser.error("Preparation and tracing options belong to the parent evaluation workflow.")
    try:
        return execute_development(args)
    except (WorkspaceError, ValueError, OllamaError, OSError, KeyboardInterrupt) as error:
        return operation_error(error)


if __name__ == "__main__":
    sys.exit(main())
