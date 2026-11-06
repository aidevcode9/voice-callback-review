"""Bounded loopback diagnostics and explicit local inference, without provisioning."""

import http.client
import json
import math
import socket
import time
from dataclasses import dataclass
from threading import Timer
from urllib.parse import urlsplit

from .domain import Failure, FailureCode, JsonValue


class OllamaError(Exception):
    def __init__(self, code: FailureCode, message: str):
        self.failure = Failure(code, message)
        super().__init__(message)


@dataclass(frozen=True)
class InstalledModel:
    name: str
    digest: str
    remote: bool = False


@dataclass(frozen=True)
class DoctorReport:
    version: str | None
    installed_models: tuple[InstalledModel, ...] | None
    failures: tuple[Failure, ...]


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        *,
        timeout: float = 3.0,
        connect_timeout: float = 1.0,
        max_response_bytes: int = 1024 * 1024,
        inference_timeout: float = 180.0,
    ):
        try:
            url = urlsplit(base_url)
            port = 11434 if url.port is None else url.port
        except ValueError:
            raise ValueError("Ollama URL must be a valid loopback HTTP URL.") from None
        if (
            url.scheme != "http"
            or url.hostname not in {"127.0.0.1", "localhost", "::1"}
            or url.username is not None
            or url.password is not None
            or url.path not in {"", "/"}
            or url.query
            or url.fragment
            or not 1 <= port <= 65535
        ):
            raise ValueError(
                "Use a loopback HTTP URL without credentials, path, query, or fragment."
            )
        if (
            not math.isfinite(timeout)
            or not 0 < timeout <= 30
            or not math.isfinite(connect_timeout)
            or not 0 < connect_timeout <= 30
        ):
            raise ValueError("Timeouts must be finite, greater than zero, and at most 30 seconds.")
        if not 1 <= max_response_bytes <= 16 * 1024 * 1024:
            raise ValueError("Response limit must be between 1 byte and 16 MiB.")
        if not math.isfinite(inference_timeout) or not 0 < inference_timeout <= 600:
            raise ValueError("Inference timeout must be finite and between 0 and 600 seconds.")
        self.host = "127.0.0.1" if url.hostname == "localhost" else url.hostname
        self.port = port
        self.timeout = timeout
        self.connect_timeout = min(connect_timeout, timeout)
        self.max_response_bytes = max_response_bytes
        self.inference_timeout = inference_timeout
        self.base_url = f"http://{'[' + self.host + ']' if ':' in self.host else self.host}:{port}"

    def _get(self, path: str) -> dict[str, JsonValue]:
        return self._request("GET", path, None, self.timeout)

    def _request(
        self, method: str, path: str, payload: dict[str, JsonValue] | None, timeout: float
    ) -> dict[str, JsonValue]:
        connection = http.client.HTTPConnection(
            self.host, self.port, timeout=min(self.connect_timeout, timeout)
        )
        deadline = time.monotonic() + timeout
        timer = None
        response = None
        try:
            connection.connect()
            transport = connection.sock

            def abort_request():
                try:
                    transport.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

            timer = Timer(max(0.001, deadline - time.monotonic()), abort_request)
            timer.daemon = True
            timer.start()
            transport.settimeout(max(0.001, deadline - time.monotonic()))
            data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
            connection.request(
                method,
                path,
                body=data,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            response = connection.getresponse()
            if 300 <= response.status < 400:
                raise OllamaError(
                    FailureCode.HTTP_ERROR,
                    "Ollama redirect refused; use the local server directly.",
                )
            body = bytearray()
            while not response.isclosed():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                transport.settimeout(remaining)
                chunk = response.read1(min(65536, self.max_response_bytes + 1 - len(body)))
                body.extend(chunk)
                if len(body) > self.max_response_bytes:
                    raise OllamaError(
                        FailureCode.INVALID_RESPONSE, "Ollama response exceeds the size limit."
                    )
                if not chunk:
                    break
            if time.monotonic() >= deadline:
                raise TimeoutError
            if response.length not in (None, 0):
                raise OllamaError(
                    FailureCode.INVALID_RESPONSE,
                    "Ollama response ended before its declared length.",
                )
            if response.status != 200:
                self._raise_http_error(response.status, path, body)
            value: JsonValue = json.loads(body.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError
            if "error" in value:
                self._raise_http_error(200, path, body)
            return value
        except TimeoutError:
            raise OllamaError(
                FailureCode.TIMEOUT,
                "Ollama timed out; check local resources and retry explicitly.",
            ) from None
        except (OSError, http.client.HTTPException):
            if time.monotonic() >= deadline:
                raise OllamaError(
                    FailureCode.TIMEOUT,
                    "Ollama timed out; check local resources and retry explicitly.",
                ) from None
            raise OllamaError(
                FailureCode.UNAVAILABLE,
                "Cannot reach Ollama; start the local server and check its loopback port.",
            ) from None
        except (ValueError, UnicodeError, RecursionError):
            raise OllamaError(
                FailureCode.INVALID_RESPONSE,
                "Ollama returned malformed JSON or an unexpected error response.",
            ) from None
        finally:
            if timer is not None:
                timer.cancel()
            if response is not None:
                response.close()
            connection.close()

    @staticmethod
    def _raise_http_error(status: int, path: str, body: bytearray) -> None:
        message = body.decode("utf-8", errors="replace").lower()
        if path == "/api/chat" and any(
            term in message
            for term in ("out of memory", "insufficient memory", "not enough memory")
        ):
            raise OllamaError(
                FailureCode.GPU_MEMORY,
                "Ollama lacks memory; release other models or reduce context.",
            )
        if path == "/api/chat" and any(
            term in message
            for term in ("context length", "context window", "context size", "input length")
        ):
            raise OllamaError(
                FailureCode.INVALID_INPUT,
                "Input exceeds the context budget; no truncation is allowed.",
            )
        if status == 404 and path in {"/api/show", "/api/chat"}:
            raise OllamaError(
                FailureCode.MODEL_MISSING, "Selected model is missing; provision it explicitly."
            )
        code = FailureCode.INVALID_RESPONSE if status == 200 else FailureCode.HTTP_ERROR
        raise OllamaError(
            code, f"Ollama returned an error for {path} (HTTP {status}); check the server."
        )

    def show(self, model_id: str) -> dict[str, JsonValue]:
        return self._request("POST", "/api/show", {"model": model_id}, self.timeout)

    def chat(self, request: dict[str, JsonValue]) -> dict[str, JsonValue]:
        return self._request("POST", "/api/chat", request, self.inference_timeout)

    def version(self) -> str:
        value = self._get("/api/version").get("version")
        if not isinstance(value, str) or not value.strip():
            raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama version is missing or invalid.")
        return value

    def installed_models(self) -> tuple[InstalledModel, ...]:
        values = self._get("/api/tags").get("models")
        if not isinstance(values, list):
            raise OllamaError(
                FailureCode.INVALID_RESPONSE,
                "Ollama models must be a list; installation status is unknown.",
            )
        result: list[InstalledModel] = []
        names: set[str] = set()
        for value in values:
            if not isinstance(value, dict):
                raise OllamaError(
                    FailureCode.INVALID_RESPONSE, "Ollama model metadata is malformed."
                )
            name, digest = value.get("name"), value.get("digest")
            if (
                not isinstance(name, str)
                or not name.strip()
                or name in names
                or not isinstance(digest, str)
                or not digest.strip()
            ):
                raise OllamaError(
                    FailureCode.INVALID_RESPONSE,
                    "Ollama model name or digest is missing, invalid, or duplicated.",
                )
            names.add(name)
            remote = (
                bool(value.get("remote_host") or value.get("remote_model"))
                or "cloud" in name.lower()
            )
            result.append(InstalledModel(name, digest, remote))
        return tuple(result)


def doctor(client: OllamaClient) -> DoctorReport:
    version = None
    installed = None
    failures: list[Failure] = []
    try:
        version = client.version()
    except OllamaError as error:
        failures.append(error.failure)
    try:
        installed = client.installed_models()
    except OllamaError as error:
        failures.append(error.failure)
    return DoctorReport(version, installed, tuple(failures))
