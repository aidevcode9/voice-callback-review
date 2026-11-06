"""Require explicit quality gates once a generated project selects its language or adds code."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ("lint", "format", "type_check", "tests")


def has_implementation(root):
    excluded = {
        ".git",
        ".venv",
        ".test-work",
        ".agents",
        ".codex",
        "assets",
        "node_modules",
        "docs",
        "data",
        "intake",
        "features",
    }
    extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".cs",
        ".rb",
        ".php",
        ".c",
        ".cpp",
        ".kt",
        ".swift",
        ".vue",
        ".svelte",
    }
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if (
            excluded.intersection(relative.parts)
            or relative.as_posix() == "scripts/check_quality_baseline.py"
        ):
            continue
        if path.is_file() and path.suffix in extensions:
            return True
    return False


def validate(root):
    config = json.loads((root / "quality-gates.json").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        return ["quality-gates.json requires schema_version 1"]
    gates = config.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATES):
        return ["quality-gates.json must list lint, format, type_check, and tests"]
    required = bool(config.get("language")) or has_implementation(root)
    if not required:
        print(
            "Quality tools deferred: documentation-only intake has no selected language or application code."
        )
        return []
    errors = []
    if not isinstance(config.get("language"), str) or not config["language"].strip():
        errors.append("Choose the implementation language in quality-gates.json")
    for name in GATES:
        gate = gates[name]
        if not isinstance(gate, dict):
            errors.append(f"Configure the {name} gate")
            continue
        command = gate.get("command")
        reason = gate.get("not_applicable_reason")
        if not (isinstance(command, str) and command.strip()) and not (
            isinstance(reason, str) and reason.strip()
        ):
            errors.append(
                f"Configure the {name} command or record an explicit not-applicable reason"
            )
    command = config.get("local_check_command")
    if not isinstance(command, str) or not command.strip():
        errors.append("Configure one shared local_check_command for local and CI use")
    ci = config.get("ci_workflow")
    if not isinstance(ci, str) or not ci.strip():
        errors.append("Configure the ci_workflow path")
    else:
        workflow = (root / ci).resolve()
        if not workflow.is_relative_to(root.resolve()) or not workflow.is_file():
            errors.append("ci_workflow must identify an existing file inside this repository")
    return errors


def main():
    try:
        errors = validate(ROOT)
    except (OSError, ValueError, TypeError) as error:
        print(f"Quality baseline configuration failed: {error}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if not errors:
        print(
            "Quality baseline configuration verified. Run the recorded checks before readiness claims."
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
