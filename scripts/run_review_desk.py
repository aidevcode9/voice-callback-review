"""Start the local production review desk; never provision models or invoke inference."""

import sys

from local_stack import ROOT, run_stack

if __name__ == "__main__":
    print("Review desk: http://127.0.0.1:8080 (Ctrl+C stops the owned local services)", flush=True)
    run_stack([sys.executable, "-m", "voice_callback.api"], 3000, ROOT, ROOT / "config/nginx.conf")
