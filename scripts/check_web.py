"""Verify locked frontend source and actual local browser/proxy/API behavior."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    node = shutil.which("node")
    if npm is None or node is None:
        raise SystemExit("Install Node.js 22.12+ before running frontend checks.")
    env = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1", "VCR_PYTHON": sys.executable}
    subprocess.run(
        [npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
        cwd=ROOT / "web",
        env=env,
        check=True,
        timeout=180,
    )
    scratch = ROOT / ".test-work"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as folder:
        target = Path(folder) / "api.generated.ts"
        subprocess.run(
            [
                node,
                str(ROOT / "web/node_modules/openapi-typescript/bin/cli.js"),
                str(ROOT / "docs/api/openapi.json"),
                "-o",
                str(target),
            ],
            cwd=ROOT,
            env=env,
            check=True,
            timeout=30,
        )
        if target.read_text(encoding="utf-8") != (ROOT / "web/lib/api.generated.ts").read_text(
            encoding="utf-8"
        ):
            raise SystemExit("Frontend contract types differ. Run npm run generate --prefix web.")
    for command in ("check", "test:browser"):
        subprocess.run([npm, "run", command], cwd=ROOT / "web", env=env, check=True, timeout=240)
    lock = json.loads((ROOT / "web/package-lock.json").read_text(encoding="utf-8"))
    if lock["lockfileVersion"] != 3:
        raise SystemExit("Expected the committed npm lockfile format.")


if __name__ == "__main__":
    main()
