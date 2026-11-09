"""Build an evaluation subprocess environment from process values and root .env.

Only the tracing keys below are read from .env. The bounded UTF-8/BOM format
accepts KEY=value, optional ``export``, blank/comment lines, literal single or
double quotes, and trailing comments after quoted values or whitespace. Quotes
do not interpret escapes; shell commands and variable references stay literal.
Process values, including empty strings, override file values. This loader never
imports an SDK, authenticates, reads legacy TXT files, or modifies os.environ.
"""

import os
import re
from collections.abc import Mapping
from pathlib import Path

TRACING_KEYS = frozenset(
    {
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_BASE_URL",
        "VCR_LANGFUSE_ENABLED",
        "VCR_LANGFUSE_CONTENT",
        "LANGFUSE_TRACING_ENABLED",
    }
)
ENVIRONMENT_LIMIT = 64 * 1024


def _assignment_value(value: str, key: str, line_number: int) -> str:
    value = value.strip()
    if "\x00" in value:
        raise ValueError(f"Invalid .env assignment for {key} on line {line_number}.")
    if not value or value.startswith("#"):
        return ""
    if value[0] not in "\"'":
        return re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
    quote = value[0]
    closing = value.find(quote, 1)
    if closing == -1:
        raise ValueError(f"Invalid .env assignment for {key} on line {line_number}.")
    remainder = value[closing + 1 :].strip()
    if remainder and not remainder.startswith("#"):
        raise ValueError(f"Invalid .env assignment for {key} on line {line_number}.")
    return value[1:closing]


def _file_values(path: Path) -> dict[str, str]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(ENVIRONMENT_LIMIT + 1)
    except FileNotFoundError:
        return {}
    except OSError:
        raise ValueError("Cannot read root .env; check the file and its permissions.") from None
    if len(raw) > ENVIRONMENT_LIMIT:
        raise ValueError("Root .env exceeds the 64 KiB size limit.")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Root .env must use UTF-8 encoding.") from None
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(content.split("\n"), start=1):
        line = raw_line.strip()
        if line.startswith("export ") or line.startswith("export\t"):
            line = line[6:].lstrip()
        match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", line)
        if match is None or match[0] not in TRACING_KEYS:
            continue
        key = match[0]
        assignment = line[len(key) :].lstrip()
        if not assignment.startswith("="):
            raise ValueError(f"Invalid .env assignment for {key} on line {line_number}.")
        values[key] = _assignment_value(assignment[1:], key, line_number)
    return values


def evaluation_environment(
    root: Path,
    *,
    tracing: bool | None = None,
    metadata_only: bool = False,
    environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Resolve tracing settings without making tracing necessary for evaluation.

    ``tracing=None`` honors VCR_LANGFUSE_ENABLED=1 from the process or .env;
    explicit True/False overrides that setting. Disabled tracing forces both
    application and SDK switches off. Enabled tracing requires no credentials
    here: the classifier retains its existing fail-open telemetry behavior.
    """
    resolved = _file_values(root / ".env")
    resolved.update(os.environ if environment is None else environment)
    enabled = resolved.get("VCR_LANGFUSE_ENABLED") == "1" if tracing is None else tracing
    resolved["VCR_LANGFUSE_ENABLED"] = "1" if enabled else "0"
    if enabled:
        resolved.setdefault("LANGFUSE_TRACING_ENABLED", "true")
    else:
        resolved["LANGFUSE_TRACING_ENABLED"] = "false"
    if metadata_only:
        resolved["VCR_LANGFUSE_CONTENT"] = "0"
    else:
        resolved.setdefault("VCR_LANGFUSE_CONTENT", "1")
    return resolved
