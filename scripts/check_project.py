"""Run the project's local and CI gates without model weights or inference."""

import argparse
import importlib.metadata
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]
SUITES = ("quality", "tests", "data", "docs", "package")


def check_tool_versions() -> None:
    for name in ("requirements-dev.txt", "requirements-runtime.txt"):
        check_locked_versions(ROOT / name)


def check_locked_versions(path: Path) -> None:
    for line in path.read_text().splitlines():
        line = line.strip().removesuffix("\\").strip()
        if not line or line.startswith(("#", "--")):
            continue
        requirement = Requirement(line)
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        installed = importlib.metadata.version(requirement.name)
        if installed not in requirement.specifier:
            raise ValueError(
                f"Install {path.name}: {requirement.name} is {installed}, expected {requirement.specifier}"
            )


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("RUN", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True, timeout=300)


def documentation_errors(root: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
    excluded = {".git", ".venv", ".test-work", "assets", "__pycache__", "build", "dist"}
    for document in root.rglob("*.md"):
        if excluded.intersection(document.relative_to(root).parts):
            continue
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            target = target.strip("<>")
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            count += 1
            if not (document.parent / unquote(target.split("#", 1)[0])).exists():
                errors.append(f"{document.relative_to(root)}: missing target {target}")
    seen: set[str] = set()
    for state in ("backlog", "active", "completed"):
        for feature in (root / "features" / state).glob("F-*"):
            feature_id = feature.name.split("-", 2)[:2]
            key = "-".join(feature_id)
            if key in seen:
                errors.append(f"Duplicate feature ID: {key}")
            seen.add(key)
            actual = {file.name for file in feature.glob("*.md")}
            substantial = {
                "01_REQUIREMENTS.md",
                "02_TECHNICAL_SPEC.md",
                "03_IMPLEMENTATION_PLAN.md",
            }
            if actual != {"FEATURE.md"} and actual != substantial:
                errors.append(f"{feature.relative_to(root)}: invalid feature document structure")
    return count, errors


def workflow_errors(root: Path) -> list[str]:
    errors: list[str] = []
    workflow = yaml.load((root / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)
    if set(workflow["on"]) != {"pull_request", "push", "workflow_dispatch"}:
        errors.append("CI requires pull_request, push, and manual triggers")
    if workflow["permissions"] != {"contents": "read"}:
        errors.append("CI requires read-only contents permission")
    expected_suites = {"quality": {"quality", "data", "docs"}, "tests": {"tests", "package"}}
    for name, suites in expected_suites.items():
        steps = workflow["jobs"][name]["steps"]
        for suite in suites:
            command = f"python scripts/check_project.py --suite {suite}"
            if not any(step.get("run", "").strip() == command for step in steps):
                errors.append(f"{name}: CI must execute shared {suite} suite")
    matrix = workflow["jobs"]["tests"]["strategy"]["matrix"]["include"]
    required_matrix = {("ubuntu-24.04", "3.10"), ("ubuntu-24.04", "3.13"), ("windows-2022", "3.13")}
    if {(entry["os"], entry["python"]) for entry in matrix} != required_matrix:
        errors.append("CI must retain the supported runtime/platform matrix")
    for name, job in workflow["jobs"].items():
        if not 1 <= int(job.get("timeout-minutes", "0")) <= 10:
            errors.append(f"{name}: missing bounded job timeout")
        for step in job["steps"]:
            if "uses" in step and not re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", step["uses"]):
                errors.append(f"{name}: action must use an immutable commit")
    return errors


def package_check() -> None:
    wheelhouse = Path(
        os.environ.get("VOICE_CALLBACK_WHEELHOUSE", ROOT / ".test-work/runtime-wheels")
    ).resolve()
    if not wheelhouse.is_dir():
        raise ValueError(
            "Prepare runtime wheels: python -m pip download --require-hashes "
            "-r requirements-runtime.txt --dest .test-work/runtime-wheels"
        )
    scratch = ROOT / ".test-work"
    scratch.mkdir(exist_ok=True)
    if not scratch.resolve().is_relative_to(ROOT):
        raise ValueError("Scratch directory escaped the repository")
    with tempfile.TemporaryDirectory(dir=scratch) as folder:
        work = Path(folder).resolve()
        if not work.is_relative_to(scratch.resolve()):
            raise ValueError("Package workspace escaped scratch directory")
        wheels = work / "wheels"
        run([sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(wheels)])
        (wheel,) = wheels.glob("*.whl")
        environment = work / "environment"
        run([sys.executable, "-m", "venv", str(environment)])
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PYTHONPATH", "PYTHONHOME"}
        }
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                "--require-hashes",
                "-r",
                str(ROOT / "requirements-runtime.txt"),
            ],
            cwd=work,
            env=env,
        )
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-index",
                "--no-deps",
                str(wheel),
            ],
            cwd=work,
            env=env,
        )
        run([str(python), "-m", "pip", "check"], cwd=work, env=env)
        run(
            [
                str(python),
                "-c",
                "import sys, voice_callback; from pathlib import Path; assert Path(voice_callback.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())",
            ],
            cwd=work,
            env=env,
        )
        run([str(python), "-m", "voice_callback.cli", "--help"], cwd=work, env=env)
        console = environment / (
            "Scripts/voice-callback.exe" if os.name == "nt" else "bin/voice-callback"
        )
        run([str(console), "--help"], cwd=work, env=env)


def check_suite(suite: str) -> None:
    python = sys.executable
    if suite == "quality":
        check_tool_versions()
        run([python, "-m", "pip", "check"])
        run([python, "-m", "ruff", "check", "src", "scripts", "tests"])
        run([python, "-m", "ruff", "format", "--check", "src", "scripts", "tests"])
        run([python, "-m", "pyright", "--pythonpath", python])
    elif suite == "tests":
        (ROOT / ".test-work").mkdir(exist_ok=True)
        run([python, "-m", "coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-v"])
        run([python, "-m", "coverage", "report"])
    elif suite == "data":
        run([python, "scripts/freeze_gold.py", "--check"])
        run([python, "scripts/check_candidates.py", "data/candidates/v0.1/cases.jsonl"])
        run(
            [
                python,
                "scripts/render_candidate_review.py",
                "data/candidates/v0.1/cases.jsonl",
                "--check",
            ]
        )
    elif suite == "docs":
        run([python, "scripts/check_quality_baseline.py"])
        count, errors = documentation_errors(ROOT)
        errors.extend(workflow_errors(ROOT))
        if errors:
            raise ValueError("\n".join(errors))
        print(f"Verified {count} local links, feature lifecycle, and CI workflow structure.")
    elif suite == "package":
        package_check()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("all", *SUITES), default="all")
    args = parser.parse_args(argv)
    try:
        for suite in SUITES if args.suite == "all" else (args.suite,):
            print(f"CHECK {suite}", flush=True)
            check_suite(suite)
    except (
        OSError,
        ValueError,
        importlib.metadata.PackageNotFoundError,
        yaml.YAMLError,
        subprocess.SubprocessError,
    ) as error:
        print(f"CHECK FAILED: {error}", file=sys.stderr)
        return 1
    print("All selected checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
