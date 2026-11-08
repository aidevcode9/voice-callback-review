"""Run the development workflow from an identified committed checkout."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .datasets import load_split
from .evaluation_environment import evaluation_environment
from .evaluation_review import assert_baseline_compatible, load_review

RELEVANT_PATHS = (
    "src",
    "config",
    "data/gold",
    "docs/CALLBACK_POLICY.md",
    "pyproject.toml",
    "requirements-runtime.txt",
    "requirements-langfuse.txt",
)


def git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments], cwd=root, capture_output=True, text=True, check=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        raise ValueError(
            "Cannot verify Git state; run this command from the project repository."
        ) from None
    return result.stdout.strip()


def repository_root() -> Path:
    return Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))


@dataclass(frozen=True)
class DevelopmentRequest:
    repository: Path
    model_id: str
    dataset: Path
    registry: Path
    policy: Path
    output: Path
    inference_lock: Path
    baseline: Path | None = None
    tracing: bool | None = None
    metadata_only: bool = False
    prepare_only: bool = False
    json_output: bool = False
    url: str = "http://127.0.0.1:11434"
    timeout: float = 3.0
    inference_timeout: float = 180.0


def _relative_input(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        raise ValueError(
            "Evaluation inputs, policy and registry must be committed inside this repository."
        ) from None


def prepare_checkout(root: Path, input_paths: tuple[Path, ...] = ()) -> Path:
    inputs = tuple(_relative_input(root, path) for path in input_paths)
    if git(root, "status", "--porcelain", "--untracked-files=all", "--", *RELEVANT_PATHS, *inputs):
        raise ValueError(
            "Commit or set aside changes to evaluation source, configuration, policy or data before running."
        )
    for path in inputs:
        if not git(root, "ls-files", "--", path):
            raise ValueError(
                "Evaluation inputs, policy and registry must be tracked in the selected commit."
            )
    revision = git(root, "rev-parse", "--verify", "HEAD")
    checkout = root / ".test-work" / "evaluation-worktrees" / revision
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        git(root, "worktree", "add", "--detach", str(checkout), revision)
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    checkout_common = git(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if (
        Path(common).resolve() != Path(checkout_common).resolve()
        or Path(git(checkout, "rev-parse", "--show-toplevel")).resolve() != checkout.resolve()
        or git(checkout, "rev-parse", "HEAD") != revision
        or git(checkout, "status", "--porcelain", "--untracked-files=all")
    ):
        raise ValueError(
            "Evaluation checkout is not the expected clean worktree; inspect it before retrying."
        )
    if not (checkout / "src/voice_callback/evaluation_worker.py").is_file():
        raise ValueError("Commit the evaluation workflow implementation before running it.")
    return checkout


def _worker_command(request: DevelopmentRequest, checkout: Path) -> list[str]:
    root = request.repository
    command = [
        sys.executable,
        "-m",
        "voice_callback.evaluation_worker",
        "evaluate",
        "--split",
        "development",
        "--model",
        request.model_id,
        "--dataset",
        str(checkout / _relative_input(root, request.dataset)),
        "--registry",
        str(checkout / _relative_input(root, request.registry)),
        "--policy",
        str(checkout / _relative_input(root, request.policy)),
        "--output-dir",
        str(request.output.resolve()),
        "--inference-lock-dir",
        str(request.inference_lock.resolve()),
        "--url",
        request.url,
        "--timeout",
        str(request.timeout),
        "--inference-timeout",
        str(request.inference_timeout),
    ]
    if request.baseline is not None:
        command.extend(("--baseline", str(request.baseline.resolve())))
    if request.json_output:
        command.append("--json")
    return command


def run_development(request: DevelopmentRequest) -> int:
    root = request.repository.resolve()
    # Reject an incompatible experiment before preparing a checkout or calling the model.
    if request.baseline is not None:
        baseline = load_review(request.baseline, request.dataset)
        assert_baseline_compatible(baseline, load_split(request.dataset, "development"))
    environment = evaluation_environment(
        root, tracing=request.tracing, metadata_only=request.metadata_only
    )
    checkout = prepare_checkout(root, (request.dataset, request.registry, request.policy))
    environment["PYTHONPATH"] = str(checkout / "src")
    environment.pop("PYTHONHOME", None)
    print(f"Development checkout: {checkout}", file=sys.stderr, flush=True)
    if request.prepare_only:
        print("Preparation complete. No inference or tracing request was made.")
        return 0
    try:
        return subprocess.run(
            _worker_command(request, checkout), cwd=checkout, env=environment, check=False
        ).returncode
    except OSError:
        raise ValueError(
            "Cannot start the evaluation worker; check the Python environment."
        ) from None
