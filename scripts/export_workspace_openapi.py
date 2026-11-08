"""Export/check API contracts without starting a server or calling a model."""

import argparse
import json
import tempfile
from pathlib import Path

from voice_callback.api import create_app

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs/api/openapi.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    scratch = ROOT / ".test-work"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as folder:
        directory = Path(folder)
        app = create_app(
            directory / "workspace.sqlite3", directory / "admission", ROOT / "config/models.json"
        )
        content = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != content:
            raise SystemExit("API schema differs; run scripts/export_workspace_openapi.py.")
        print("Workspace OpenAPI matches the implemented routes.")
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(content, encoding="utf-8")
        print(f"Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
