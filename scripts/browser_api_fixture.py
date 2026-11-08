"""Browser-test-only Ollama HTTP fixture and API. No frozen cases, answers or real runtime."""

import json
import os
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import uvicorn

from voice_callback.admission import InferenceAdmission
from voice_callback.api import create_app
from voice_callback.jobs import local_classifier
from voice_callback.ollama import OllamaClient

ROOT = Path(__file__).resolve().parents[1]
TAG = "qwen3.5:4b-q4_K_M"


def main(directory: Path) -> None:
    control_secret = os.environ["VCR_FIXTURE_CONTROL_SECRET"]
    if not control_secret:
        raise SystemExit("Fixture control secret is required.")
    runtime = OllamaClient("http://127.0.0.1:18735", inference_timeout=30)
    admission = InferenceAdmission(directory / "admission")
    state = {"mode": "success", "outcome": "callback_required", "chats": 0, "active": 0}
    released = threading.Event()
    released.set()
    server_holder: list[uvicorn.Server] = []
    restart = threading.Event()
    classify = local_classifier(runtime, ROOT / "docs/CALLBACK_POLICY.md")

    def controlled_classifier(transcript, model):
        if state["mode"] == "worker_error":
            raise RuntimeError("Controlled worker interruption")
        return classify(transcript, model)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def reply(self, value: object, status: int = 200) -> None:
            data = json.dumps(value).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except OSError:
                pass

        def authorized_control(self) -> bool:
            supplied = self.headers.get("X-Fixture-Control", "")
            return secrets.compare_digest(supplied.encode(), control_secret.encode())

        def do_GET(self) -> None:
            if self.path == "/control":
                if not self.authorized_control():
                    self.reply({"error": "Forbidden"}, 403)
                    return
                self.reply(state)
            elif state["mode"] == "unavailable":
                self.reply({"error": "Controlled runtime unavailable"}, 503)
            elif self.path == "/api/version":
                self.reply({"version": "0.40.15"})
            elif self.path == "/api/tags":
                self.reply({"models": [{"name": TAG, "digest": "controlled-browser-fixture"}]})
            else:
                self.reply({}, 404)

        def do_POST(self) -> None:
            if self.path == "/control" and not self.authorized_control():
                self.reply({"error": "Forbidden"}, 403)
                return
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            if self.path == "/control":
                action = body.get("action")
                if action == "release":
                    released.set()
                elif action == "recover":
                    if state["active"]:
                        self.reply({"error": "Fixture request still active"}, 409)
                        return
                    admission.recover()
                elif action == "restart":
                    released.set()
                    restart.set()
                    server_holder[0].should_exit = True
                else:
                    state["mode"] = body.get("mode", "success")
                    state["outcome"] = body.get("outcome", "callback_required")
                    runtime.inference_timeout = 0.2 if state["mode"] == "timeout" else 30
                    if state["mode"] == "hold":
                        released.clear()
                self.reply(state)
                return
            if self.path == "/api/show":
                self.reply(
                    {
                        "details": {"format": "gguf", "family": "qwen35"},
                        "capabilities": ["completion", "thinking"],
                        "thinking": {"values": [False, True]},
                        "model_info": {
                            "general.architecture": "qwen35",
                            "qwen35.context_length": 262144,
                        },
                    }
                )
                return
            if self.path != "/api/chat":
                self.reply({}, 404)
                return
            state["chats"] += 1
            state["active"] += 1
            try:
                if state["mode"] == "hold":
                    released.wait(20)
                if state["mode"] == "timeout":
                    time.sleep(0.6)
                text = json.loads(body["messages"][1]["content"])["transcript"]
                label = state["outcome"]
                rule = {
                    "callback_required": "CB-002",
                    "no_callback": "NC-001",
                    "needs_review": "NR-001",
                }[label]
                quotes = (
                    ["Please call me back.", "Please call me"]
                    if "Please call me back." in text
                    else [text.split("\n")[0]]
                )
                content = (
                    "malformed"
                    if state["mode"] == "malformed"
                    else json.dumps(
                        {
                            "label": label,
                            "rule_ids": [rule],
                            "reason": "Controlled browser-verification response; not a model-quality judgment.",
                            "evidence": quotes,
                        }
                    )
                )
                self.reply(
                    {
                        "model": TAG,
                        "done": True,
                        "done_reason": "stop",
                        "message": {"role": "assistant", "content": content},
                    }
                )
            finally:
                state["active"] -= 1

    http = ThreadingHTTPServer(("127.0.0.1", 18735), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        while True:
            app = create_app(
                directory / "workspace.sqlite3",
                directory / "admission",
                ROOT / "config/models.json",
                client=runtime,
                classifier=controlled_classifier,
                origins=("http://127.0.0.1:18880",),
                verification_mode="controlled",
            )
            server = uvicorn.Server(
                uvicorn.Config(
                    app, host="127.0.0.1", port=18700, log_level="warning", access_log=False
                )
            )
            server_holder[:] = [server]
            server.run()
            if not restart.is_set():
                break
            restart.clear()
    finally:
        released.set()
        http.shutdown()
        http.server_close()
        thread.join(timeout=3)


if __name__ == "__main__":
    directory = Path(sys.argv[1]).resolve()
    if not directory.is_relative_to(ROOT / ".test-work"):
        raise SystemExit("Browser fixture storage must be isolated below .test-work.")
    main(directory)
