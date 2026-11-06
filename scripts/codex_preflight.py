"""Validate the staged index or current commit, independently of dirty working files."""

import argparse
import io
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export_tree(root: Path, target: Path, mode: str) -> None:
    if mode == "pre-commit":
        entries = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=root)
        if any(entry.startswith(b"120000 ") for entry in entries.split(b"\0")):
            raise ValueError("Snapshot checks do not accept symbolic links")
        subprocess.run(["git", "diff", "--cached", "--check"], cwd=root, check=True)
        subprocess.run(
            ["git", "checkout-index", "--all", f"--prefix={target.as_posix()}/"],
            cwd=root,
            check=True,
        )
    else:
        archive = subprocess.check_output(["git", "archive", "--format=zip", "HEAD"], cwd=root)
        with zipfile.ZipFile(io.BytesIO(archive)) as snapshot:
            for entry in snapshot.infolist():
                if not (target / entry.filename).resolve().is_relative_to(target.resolve()):
                    raise ValueError("Git archive path escaped its destination")
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Snapshot checks do not accept symbolic links")
            snapshot.extractall(target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pre-commit", "pre-push", "review"), required=True)
    args = parser.parse_args(argv)
    scratch = ROOT / ".test-work"
    scratch.mkdir(exist_ok=True)
    try:
        if not scratch.resolve().is_relative_to(ROOT):
            raise ValueError("Scratch directory escaped the repository")
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            snapshot = Path(folder).resolve()
            if not snapshot.is_relative_to(scratch.resolve()):
                raise ValueError("Preflight workspace escaped scratch directory")
            export_tree(ROOT, snapshot, args.mode)
            checker = snapshot / "scripts/check_project.py"
            if not checker.is_file():
                raise ValueError(
                    "Selected tree has no quality runner; stage or commit the baseline first"
                )
            env = {**os.environ, "PYTHONPATH": str(snapshot / "src")}
            print(f"Validating {args.mode} snapshot, not the working directory.", flush=True)
            subprocess.run(
                [sys.executable, str(checker)], cwd=snapshot, env=env, check=True, timeout=900
            )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"PREFLIGHT FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
