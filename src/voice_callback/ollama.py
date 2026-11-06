"""Read-only loopback Ollama diagnostics, with no SDK, credentials, or inference."""

from dataclasses import dataclass
import http.client
import json
import math
import socket
import time
from threading import Timer
from urllib.parse import urlsplit

from .domain import Failure, FailureCode


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
    def __init__(self, base_url: str = "http://127.0.0.1:11434", *,
                 timeout: float = 3.0, connect_timeout: float = 1.0,
                 max_response_bytes: int = 1024 * 1024):
        try:
            url = urlsplit(base_url)
            port = 11434 if url.port is None else url.port
        except ValueError:
            raise ValueError("Ollama URL must be a valid loopback HTTP URL.") from None
        if (url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost", "::1"}
                or url.username is not None or url.password is not None
                or url.path not in {"", "/"} or url.query or url.fragment
                or not 1 <= port <= 65535):
            raise ValueError("Use a loopback HTTP URL without credentials, path, query, or fragment.")
        if (not math.isfinite(timeout) or not 0 < timeout <= 30
                or not math.isfinite(connect_timeout) or not 0 < connect_timeout <= 30):
            raise ValueError("Timeouts must be finite, greater than zero, and at most 30 seconds.")
        if not 1 <= max_response_bytes <= 16 * 1024 * 1024:
            raise ValueError("Response limit must be between 1 byte and 16 MiB.")
        self.host = "127.0.0.1" if url.hostname == "localhost" else url.hostname
        self.port = port
        self.timeout = timeout
        self.connect_timeout = min(connect_timeout, timeout)
        self.max_response_bytes = max_response_bytes

    def _get(self, path: str) -> dict:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.connect_timeout)
        deadline = time.monotonic() + self.timeout
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
            connection.request("GET", path, headers={"Accept": "application/json"})
            response = connection.getresponse()
            if response.status != 200:
                raise OllamaError(FailureCode.HTTP_ERROR,
                                  f"Ollama returned HTTP {response.status} for {path}; check the local server.")
            body = bytearray()
            while not response.isclosed():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                transport.settimeout(remaining)
                chunk = response.read1(min(65536, self.max_response_bytes + 1 - len(body)))
                body.extend(chunk)
                if len(body) > self.max_response_bytes:
                    raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama response exceeds the size limit.")
                if not chunk:
                    break
            if time.monotonic() >= deadline:
                raise TimeoutError
            if response.length not in (None, 0):
                raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama response ended before its declared length.")
            value = json.loads(body.decode("utf-8"))
            if not isinstance(value, dict) or "error" in value:
                raise ValueError
            return value
        except (TimeoutError, socket.timeout):
            raise OllamaError(FailureCode.TIMEOUT, "Ollama timed out; check the local server and retry diagnostics.") from None
        except (OSError, http.client.HTTPException):
            if time.monotonic() >= deadline:
                raise OllamaError(FailureCode.TIMEOUT, "Ollama timed out; check the local server and retry diagnostics.") from None
            raise OllamaError(FailureCode.UNAVAILABLE, "Cannot reach Ollama; start the local server and check its loopback port.") from None
        except (ValueError, UnicodeError, RecursionError):
            raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama returned malformed JSON or an unexpected error response.") from None
        finally:
            if timer is not None:
                timer.cancel()
            if response is not None:
                response.close()
            connection.close()

    def version(self) -> str:
        value = self._get("/api/version").get("version")
        if not isinstance(value, str) or not value.strip():
            raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama version is missing or invalid.")
        return value

    def installed_models(self) -> tuple[InstalledModel, ...]:
        values = self._get("/api/tags").get("models")
        if not isinstance(values, list):
            raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama models must be a list; installation status is unknown.")
        result = []
        names = set()
        for value in values:
            if not isinstance(value, dict):
                raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama model metadata is malformed.")
            name, digest = value.get("name"), value.get("digest")
            if (not isinstance(name, str) or not name.strip() or name in names
                    or not isinstance(digest, str) or not digest.strip()):
                raise OllamaError(FailureCode.INVALID_RESPONSE, "Ollama model name or digest is missing, invalid, or duplicated.")
            names.add(name)
            remote = bool(value.get("remote_host") or value.get("remote_model")) or "cloud" in name.lower()
            result.append(InstalledModel(name, digest, remote))
        return tuple(result)


def doctor(client: OllamaClient) -> DoctorReport:
    version, installed = None, None
    failures = []
    for method, target in ((client.version, "version"), (client.installed_models, "models")):
        try:
            value = method()
            if target == "version":
                version = value
            else:
                installed = value
        except OllamaError as error:
            failures.append(error.failure)
    return DoctorReport(version, installed, tuple(failures))
