"""Isolated real web/proxy/API stack with a controlled HTTP runtime, never a model."""

import sys
import tempfile
from pathlib import Path

from local_stack import ROOT, run_stack

if __name__ == "__main__":
    scratch = ROOT / ".test-work"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-", dir=scratch) as folder:
        prefix = Path(folder)
        config = prefix / "nginx.conf"
        text = (ROOT / "config/nginx.conf").read_text(encoding="utf-8")
        text = text.replace(":8080", ":18880").replace(":8000", ":18700").replace(":3000", ":18730")
        config.write_text(text, encoding="utf-8")
        run_stack(
            [sys.executable, str(ROOT / "scripts/browser_api_fixture.py"), str(prefix)],
            18730,
            prefix,
            config,
        )
