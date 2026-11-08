"""Explicitly provision the hash-pinned official Windows Nginx tool, never models."""

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://nginx.org/download/nginx-1.31.8.zip"
SHA256 = "fbb1501009be34655cc238d460714cf20391b639013f4c73859813d7938783fd"


def main() -> None:
    if sys.platform != "win32":
        raise SystemExit("Use your system Nginx package on Linux/macOS and set NGINX_EXECUTABLE.")
    tools = (ROOT / ".test-work/tools").resolve()
    if not tools.is_relative_to(ROOT):
        raise ValueError("Tool directory escaped the repository.")
    tools.mkdir(parents=True, exist_ok=True)
    archive = tools / "nginx-1.31.8.zip"
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read(10 * 1024 * 1024 + 1)
        if len(data) > 10 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("Nginx archive size/hash did not match the pinned tool.")
        archive.write_bytes(data)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Nginx archive hash differs; preserve it for inspection.")
    with zipfile.ZipFile(archive) as package:
        for entry in package.infolist():
            if not (tools / entry.filename).resolve().is_relative_to(tools):
                raise ValueError("Archive entry escaped the tool directory.")
        package.extractall(tools)
    print("Verified and provisioned Nginx 1.31.8 under .test-work/tools.")


if __name__ == "__main__":
    main()
