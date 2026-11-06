"""Exercise actual HTTP and CLI boundaries against controlled loopback responses."""

import json
import subprocess
import sys
import threading
import time
import unittest
from contextlib import contextmanager, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from unittest.mock import patch

from voice_callback.cli import main
from voice_callback.domain import FailureCode
from voice_callback.ollama import OllamaClient, OllamaError, doctor


@contextmanager
def server(routes):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.command, self.path))
            status, payload, delay, *body_options = routes.get(self.path, (404, {}, 0))
            body_delay = body_options[0] if body_options else 0
            length_offset = body_options[1] if len(body_options) > 1 else 0
            time.sleep(delay)
            body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Length", str(len(body) + length_offset))
                if status == 302:
                    self.send_header("Location", "https://example.com/cloud")
                self.end_headers()
                if body_delay:
                    for byte in body:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        time.sleep(body_delay)
                else:
                    self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

        def log_message(self, format: str, *args: object) -> None:
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    worker.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}", requests
    finally:
        httpd.shutdown()
        httpd.server_close()
        worker.join(timeout=2)


def routes(models=None):
    return {
        "/api/version": (200, {"version": "test-1"}, 0),
        "/api/tags": (200, {"models": [] if models is None else models}, 0),
    }


class OllamaBehavior(unittest.TestCase):
    def test_empty_server_is_observed_without_inference(self):
        with server(routes()) as (url, requests):
            report = doctor(OllamaClient(url))
        self.assertEqual(report.version, "test-1")
        self.assertEqual(report.installed_models, ())
        self.assertEqual(report.failures, ())
        self.assertEqual(requests, [("GET", "/api/version"), ("GET", "/api/tags")])

    def test_populated_models_preserve_identity_and_remote_status(self):
        data = [
            {"name": "local:4b", "digest": "sha256:abc"},
            {"name": "remote", "digest": "sha256:def", "remote_host": "https://ollama.com"},
        ]
        with server(routes(data)) as (url, _):
            observed = OllamaClient(url).installed_models()
        self.assertEqual(observed[0].digest, "sha256:abc")
        self.assertFalse(observed[0].remote)
        self.assertTrue(observed[1].remote)

    def test_connection_refused_is_not_an_empty_model_list(self):
        with patch("http.client.HTTPConnection.connect", side_effect=ConnectionRefusedError):
            report = doctor(OllamaClient(timeout=0.2))
        self.assertIsNone(report.installed_models)
        self.assertEqual([f.code for f in report.failures], [FailureCode.UNAVAILABLE] * 2)

    def test_timeout_is_explicit(self):
        with server({"/api/version": (200, {"version": "late"}, 0.2)}) as (url, _):
            with self.assertRaises(OllamaError) as caught:
                OllamaClient(url, timeout=0.03).version()
        self.assertEqual(caught.exception.failure.code, FailureCode.TIMEOUT)

    def test_continuous_slow_body_is_stopped_by_total_deadline(self):
        with server({"/api/version": (200, {"version": "slow"}, 0, 0.02)}) as (url, _):
            with self.assertRaises(OllamaError) as caught:
                OllamaClient(url, timeout=0.06).version()
        self.assertEqual(caught.exception.failure.code, FailureCode.TIMEOUT)

    def test_http_error_and_redirect_are_not_followed_or_echoed(self):
        for status in (302, 404, 500):
            with (
                self.subTest(status=status),
                server({"/api/version": (status, {"error": "sensitive"}, 0)}) as (url, requests),
            ):
                with self.assertRaises(OllamaError) as caught:
                    OllamaClient(url).version()
            self.assertEqual(caught.exception.failure.code, FailureCode.HTTP_ERROR)
            self.assertNotIn("sensitive", str(caught.exception))
            self.assertEqual(requests, [("GET", "/api/version")])

    def test_malformed_json_and_version_schema_are_failures(self):
        for payload in (
            b"not-json",
            b"\xff",
            [],
            {"version": 3},
            {"version": ""},
            {"error": "private"},
        ):
            with (
                self.subTest(payload=payload),
                server({"/api/version": (200, payload, 0)}) as (url, _),
            ):
                with self.assertRaises(OllamaError) as caught:
                    OllamaClient(url).version()
            self.assertEqual(caught.exception.failure.code, FailureCode.INVALID_RESPONSE)

    def test_missing_or_malformed_model_list_does_not_claim_empty(self):
        for payload in (
            {},
            {"models": None},
            {"models": {}},
            {"models": [None]},
            {"models": [{"name": "x"}]},
            {"models": [{"name": "x", "digest": "a"}] * 2},
        ):
            with self.subTest(payload=payload):
                fixtures = routes()
                fixtures["/api/tags"] = (200, payload, 0)
                with server(fixtures) as (url, _):
                    report = doctor(OllamaClient(url))
                self.assertEqual(report.version, "test-1")
                self.assertIsNone(report.installed_models)
                self.assertEqual(report.failures[0].code, FailureCode.INVALID_RESPONSE)

    def test_premature_end_of_body_is_not_success_even_if_json_is_valid(self):
        with server({"/api/version": (200, {"version": "test"}, 0, 0, 10)}) as (url, _):
            with self.assertRaises(OllamaError) as caught:
                OllamaClient(url).version()
        self.assertEqual(caught.exception.failure.code, FailureCode.INVALID_RESPONSE)

    def test_response_size_is_bounded(self):
        with server(routes()) as (url, _):
            with self.assertRaises(OllamaError) as caught:
                OllamaClient(url, max_response_bytes=4).version()
        self.assertEqual(caught.exception.failure.code, FailureCode.INVALID_RESPONSE)

    def test_remote_urls_credentials_and_unbounded_timeouts_are_rejected(self):
        for url in (
            "https://127.0.0.1",
            "http://example.com",
            "http://127.0.0.1@evil.com",
            "http://user:secret@localhost",
            "http://localhost/api",
            "http://localhost?x=1",
            "http://localhost#x",
            "http://localhost:abc",
            "http://localhost:0",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                OllamaClient(url)
        for timeout in (0, -1, float("nan"), float("inf"), 31):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                OllamaClient(timeout=timeout)


class DiagnosticCLI(unittest.TestCase):
    def invoke(self, args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(args)
        return code, json.loads(output.getvalue())

    def test_doctor_empty_state_is_successful_diagnostic_only(self):
        with server(routes()) as (url, requests):
            code, result = self.invoke(["doctor", "--url", url])
        self.assertEqual(code, 0)
        self.assertEqual(result["installed_models"], [])
        self.assertFalse(result["inference_verified"])
        self.assertIn("zero installed models", " ".join(result["messages"]))
        self.assertEqual(len(requests), 2)

    def test_classification_selector_has_no_invented_default(self):
        with server(routes()) as (url, _):
            code, result = self.invoke(["models", "--stage", "classification", "--url", url])
        self.assertEqual(code, 0)
        self.assertEqual(result["configured_models"], [])
        self.assertIn("No classifier is configured", " ".join(result["messages"]))

    def test_transcription_candidates_are_unverified_and_not_selectable(self):
        with server(routes()) as (url, _):
            code, result = self.invoke(["models", "--stage", "transcription", "--url", url])
        self.assertEqual(code, 0)
        self.assertEqual(len(result["configured_models"]), 2)
        self.assertTrue(
            all(
                row["availability"] == "runtime_not_verified" and not row["selectable"]
                for row in result["configured_models"]
            )
        )

    def test_http_failure_returns_exit_one_and_unknown_installation(self):
        with server({}) as (url, _):
            code, result = self.invoke(["doctor", "--url", url])
        self.assertEqual(code, 1)
        self.assertIsNone(result["installed_models"])
        self.assertEqual(result["status"], "diagnostic_error")

    def test_configuration_failure_returns_exit_two_without_network(self):
        code, result = self.invoke(["doctor", "--url", "https://example.com"])
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "configuration_error")
        code, result = self.invoke(["doctor", "--registry", "missing-registry.json"])
        self.assertEqual(code, 2)

    def test_module_entrypoint_process_exit_and_json(self):
        with server(routes()) as (url, _):
            result = subprocess.run(
                [sys.executable, "-m", "voice_callback.cli", "doctor", "--url", url],
                capture_output=True,
                text=True,
                timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["server_version"], "test-1")
