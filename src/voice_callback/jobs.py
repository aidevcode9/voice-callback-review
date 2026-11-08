"""Admit a single durable job and delegate its work to the existing classifier."""

import sqlite3
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .admission import InferenceAdmission, InferenceLease, provider_quiescent
from .classify import classify
from .contracts import ModelEntry
from .domain import ModelConfig, RunResult, Stage, TranscriptOrigin, TranscriptVersion
from .evaluation_config import source_identity
from .ollama import OllamaClient
from .storage import render_json
from .workspace import Workspace, WorkspaceError
from .workspace_contracts import JobRecord, SubmitJob, VersionRecord

Classifier = Callable[[TranscriptVersion, ModelConfig], RunResult]


class JobService:
    def __init__(
        self,
        workspace: Workspace,
        admission: InferenceAdmission,
        models: tuple[ModelConfig, ...],
        classifier: Classifier,
    ):
        self.workspace, self.admission = workspace, admission
        self.models, self.classifier = models, classifier
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="callback")
        self.mutex = threading.Lock()
        self.reconciled = False
        self.reconcile()

    def reconcile(self) -> None:
        with self.mutex:
            if self.reconciled:
                return
            try:
                lease = self.admission.lock()
            except WorkspaceError:
                return
            try:
                self.workspace.interrupt_jobs()
                self.reconciled = True
            finally:
                lease.close()

    def submit(self, key: str, request: SubmitJob) -> JobRecord:
        self.reconcile()
        with self.mutex:
            previous = self.workspace.previous_job(key, request)
            if previous:
                return previous
            models = [
                m
                for m in self.models
                if m.id == request.model_config_id and Stage.CLASSIFICATION in m.stages
            ]
            if not models:
                raise WorkspaceError(
                    "invalid_model", 422, "Choose an explicitly configured classifier."
                )
            model = models[0]
            lease = self.admission.acquire()
            try:
                job = self.workspace.create_job(
                    key,
                    request,
                    ModelEntry.model_validate_json(render_json(model)),
                    source_identity(),
                )
            except Exception:
                lease.close(completed=True)
                raise
            try:
                self.executor.submit(self._execute, job, model, lease)
            except RuntimeError:
                self.workspace.interrupt_jobs()
                lease.close(completed=True)
                raise WorkspaceError(
                    "service_stopping", 503, "The API is stopping; reconnect before submitting."
                ) from None
            return job

    def _execute(self, job: JobRecord, model: ModelConfig, lease: InferenceLease) -> None:
        completed = False
        try:
            version = self.workspace.get("version", job.transcript_version_id, VersionRecord)
            transcript = TranscriptVersion(
                job.case_id,
                version.id,
                version.text,
                TranscriptOrigin.CORRECTION if version.parent_version_id else TranscriptOrigin.TEXT,
                version.parent_version_id,
            )
            result = self.classifier(transcript, model)
            self.workspace.complete_job(
                job.id, result, recovery_required=not provider_quiescent(result)
            )
            completed = provider_quiescent(result)
        except Exception:
            # An unknown worker/storage failure cannot prove provider quiescence.
            with self.mutex:
                self.reconciled = False
            try:
                self.workspace.interrupt_jobs()
            except (OSError, sqlite3.Error):
                pass  # Reconcile on a later request after storage recovers.
        finally:
            lease.close(completed=completed)

    def close(self) -> None:
        self.executor.shutdown(wait=True)


def local_classifier(client: OllamaClient, policy: Path) -> Classifier:
    def run(transcript: TranscriptVersion, model: ModelConfig) -> RunResult:
        return classify(transcript, model, client, policy_path=policy)

    return run
