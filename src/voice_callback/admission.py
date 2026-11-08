"""One local inference owner across CLI/API processes; crashes require explicit recovery."""

import json
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from .domain import FailureCode, RunFailure, RunResult
from .workspace import WorkspaceError

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl


def provider_quiescent(result: RunResult) -> bool:
    return not (
        isinstance(result, RunFailure)
        and result.failure.code
        in {
            FailureCode.TIMEOUT,
            FailureCode.UNAVAILABLE,
            FailureCode.HTTP_ERROR,
            FailureCode.INVALID_RESPONSE,
        }
    )


class InferenceLease:
    def __init__(self, stream: BinaryIO, marker: Path):
        self.stream, self.marker = stream, marker
        self.recovery_required = False

    def observe(self, result: RunResult) -> None:
        self.recovery_required = self.recovery_required or not provider_quiescent(result)

    def close(self, *, completed: bool = False) -> None:
        try:
            if completed:
                self.marker.unlink(missing_ok=True)
        finally:
            self.stream.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()


class InferenceAdmission:
    def __init__(self, directory: Path = Path("runtime/inference")):
        self.directory = directory
        self.marker = directory / "pending.json"

    def lock(self) -> InferenceLease:
        self.directory.mkdir(parents=True, exist_ok=True)
        stream = (self.directory / "admission.lock").open("a+b")
        try:
            if stream.seek(0, 2) == 0:
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            stream.close()
            raise WorkspaceError(
                "job_busy", 409, "Another local inference operation is active."
            ) from None
        return InferenceLease(stream, self.marker)

    def acquire(self) -> InferenceLease:
        lease = self.lock()
        try:
            if self.marker.exists():
                raise WorkspaceError(
                    "recovery_required",
                    503,
                    "A previous operation was interrupted. Stop the local runtime and explicitly recover admission.",
                )
            with self.marker.open("x", encoding="utf-8") as stream:
                json.dump({"pid": os.getpid()}, stream)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            lease.close()
            raise
        return lease

    @contextmanager
    def operation(self) -> Generator[InferenceLease, None, None]:
        lease = self.acquire()
        try:
            yield lease
        except ValueError:
            lease.close(completed=not lease.recovery_required)
            raise
        except BaseException:
            lease.close()
            raise
        else:
            lease.close(completed=not lease.recovery_required)

    def recover(self) -> None:
        """Caller must explicitly confirm the runtime is stopped, never infer it from time."""
        self.lock().close(completed=True)

    def stale(self) -> bool:
        try:
            lease = self.lock()
        except WorkspaceError:
            return False
        try:
            return self.marker.exists()
        finally:
            lease.close()

    def status(self) -> str:
        try:
            lease = self.lock()
        except WorkspaceError:
            return "busy"
        try:
            return "recovery_required" if self.marker.exists() else "ready"
        finally:
            lease.close()
