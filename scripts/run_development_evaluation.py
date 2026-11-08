"""Compatibility entry point; use voice-callback evaluate --model MODEL_ID."""

import sys

from voice_callback.cli import main as cli_main


def main(argv: list[str] | None = None) -> int:
    print(
        "Use voice-callback evaluate --model MODEL_ID for the evaluation workflow.", file=sys.stderr
    )
    return cli_main(["evaluate", *(sys.argv[1:] if argv is None else argv)])


if __name__ == "__main__":
    raise SystemExit(main())
