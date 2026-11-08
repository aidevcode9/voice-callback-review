"""Own and stop only the loopback processes started for one local stack."""

import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def nginx_executable() -> str:
    configured = os.environ.get("NGINX_EXECUTABLE") or shutil.which("nginx")
    portable = ROOT / ".test-work/tools/nginx-1.31.8/nginx.exe"
    if configured:
        return configured
    if portable.is_file():
        return str(portable)
    raise SystemExit("Set NGINX_EXECUTABLE to an installed Nginx binary; see docs/LOCAL_SETUP.md.")


def run_stack(api_command: list[str], next_port: int, prefix: Path, config: Path) -> None:
    node = shutil.which("node")
    if node is None:
        raise SystemExit("Node.js is required.")
    if not (ROOT / "web/.next/BUILD_ID").is_file():
        raise SystemExit("Build the frontend first: npm run build --prefix web")
    prefix = prefix.resolve()
    if not prefix.is_relative_to(ROOT):
        raise ValueError("Local stack prefix must stay within the repository.")
    (prefix / "runtime").mkdir(parents=True, exist_ok=True)
    prefix = Path(tempfile.mkdtemp(prefix="stack-", dir=prefix / "runtime"))
    (prefix / "runtime").mkdir()
    print(f"Nginx log: {prefix / 'runtime/nginx-error.log'}", flush=True)
    nginx = nginx_executable()
    arguments = [
        nginx,
        "-p",
        prefix.as_posix() + "/",
        "-c",
        config.resolve().as_posix(),
        "-e",
        (prefix / "runtime/nginx-error.log").as_posix(),
    ]
    subprocess.run([*arguments, "-t"], check=True, timeout=10)
    stopped = False

    def stop(signum: int, frame: object) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    env = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1", "PYTHONUNBUFFERED": "1"}
    processes: list[subprocess.Popen[bytes]] = []
    try:
        processes.append(subprocess.Popen(api_command, cwd=ROOT, env=env))
        processes.append(
            subprocess.Popen(
                [
                    node,
                    str(ROOT / "web/node_modules/next/dist/bin/next"),
                    "start",
                    "--hostname",
                    "127.0.0.1",
                    "--port",
                    str(next_port),
                ],
                cwd=ROOT / "web",
                env=env,
            )
        )
        processes.append(subprocess.Popen([*arguments, "-g", "daemon off;"], cwd=prefix, env=env))
        while not stopped:
            for process in processes:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"Owned local service exited with code {process.returncode}."
                    )
            time.sleep(0.2)
    finally:
        if (prefix / "runtime/nginx.pid").exists():
            subprocess.run([*arguments, "-s", "quit"], timeout=10, check=False)
        if processes:
            try:
                processes[-1].wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
