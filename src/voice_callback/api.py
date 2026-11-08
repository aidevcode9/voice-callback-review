"""Thin loopback API over the existing classifier and local workspace services."""

import secrets
import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .admission import InferenceAdmission
from .contracts import RunFailureRecord, RunSuccessRecord
from .development_cases import DEVELOPMENT_CASES
from .jobs import Classifier, JobService, local_classifier
from .json_io import parse_json
from .models import list_models, load_registry
from .ollama import OllamaClient, doctor
from .workspace import Workspace, WorkspaceError
from .workspace_contracts import (
    CaseDetail,
    CaseRecord,
    CaseSummary,
    CreateCase,
    CreatedCase,
    CreateReview,
    CreateVersion,
    DevelopmentSummary,
    EmptyRequest,
    JobRecord,
    ReviewRecord,
    RuntimeReport,
    Session,
    SubmitJob,
    VersionRecord,
    VersionSummary,
)

MAX_REQUEST_BYTES = 65536


def error_response(code: str, status: int, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


class LocalBoundary:
    def __init__(self, app: ASGIApp, origins: tuple[str, ...], nonce: str):
        self.app, self.origins, self.nonce = app, origins, nonce

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive)
        host = request.headers.get("host", "")
        origin = request.headers.get("origin")
        expected = f"http://{host}"
        if expected not in self.origins or (origin is not None and origin != expected):
            await error_response(
                "invalid_origin", 403, "Use the configured local workspace origin."
            )(scope, receive, send)
            return
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if origin != expected or not secrets.compare_digest(
                request.headers.get("x-workspace-nonce", "").encode("utf-8"),
                self.nonce.encode("ascii"),
            ):
                await error_response("invalid_session", 403, "Reload the local workspace session.")(
                    scope, receive, send
                )
                return
            if request.headers.get("content-type", "").split(";", 1)[0] != "application/json":
                await error_response("invalid_content_type", 415, "Submit application/json.")(
                    scope, receive, send
                )
                return
            raw = bytearray()
            more = True
            while more:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                raw.extend(message.get("body", b""))
                if len(raw) > MAX_REQUEST_BYTES:
                    await error_response("payload_too_large", 413, "Request exceeds 64 KiB.")(
                        scope, receive, send
                    )
                    return
                more = message.get("more_body", False)
            try:
                parse_json(raw.decode("utf-8"))
            except (ValueError, UnicodeError, RecursionError):
                await error_response("invalid_json", 400, "Submit one strict UTF-8 JSON document.")(
                    scope, receive, send
                )
                return

            async def replay() -> Message:
                return {"type": "http.request", "body": bytes(raw), "more_body": False}

            receive = replay
        await self.app(scope, receive, send)


def create_app(
    workspace_path: Path = Path("runtime/workspace/workspace.sqlite3"),
    admission_path: Path = Path("runtime/inference"),
    registry_path: Path = Path("config/models.json"),
    policy_path: Path = Path("docs/CALLBACK_POLICY.md"),
    *,
    classifier: Classifier | None = None,
    client: OllamaClient | None = None,
    verification_mode: Literal["live", "controlled"] = "live",
    origins: tuple[str, ...] = ("http://127.0.0.1:8000", "http://127.0.0.1:8080"),
) -> FastAPI:
    workspace = Workspace(workspace_path)
    runtime = client or OllamaClient("http://127.0.0.1:11434")
    configs = load_registry(registry_path)
    jobs = JobService(
        workspace,
        InferenceAdmission(admission_path),
        configs,
        classifier or local_classifier(runtime, policy_path),
    )
    nonce = secrets.token_urlsafe(32)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        yield
        jobs.close()

    app = FastAPI(
        title="Voice Callback Review local API",
        version="1.0",
        lifespan=lifespan,
        dependencies=[Depends(jobs.reconcile)],
    )
    app.add_middleware(LocalBoundary, origins=origins, nonce=nonce)

    @app.exception_handler(WorkspaceError)
    async def workspace_error(request: Request, error: WorkspaceError) -> JSONResponse:
        return error_response(error.code, error.status, error.message)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError) -> JSONResponse:
        return error_response(
            "invalid_request", 422, "Check the required fields, types and input limits."
        )

    @app.exception_handler(sqlite3.Error)
    @app.exception_handler(OSError)
    @app.exception_handler(ValueError)
    async def storage_error(request: Request, error: Exception) -> JSONResponse:
        return error_response(
            "storage_unavailable",
            503,
            "Cannot save workspace records; check local storage before retrying.",
        )

    @app.get("/api/v1/session", response_model=Session)
    def session() -> JSONResponse:
        return JSONResponse({"nonce": nonce}, headers={"Cache-Control": "no-store"})

    @app.get("/api/v1/runtime", response_model=RuntimeReport)
    def runtime_status() -> JSONResponse:
        report = doctor(runtime)
        choices = list_models(configs, report.installed_models)
        return JSONResponse(
            {
                "status": "unavailable" if report.failures else "available",
                "server_version": report.version,
                "models": [
                    {
                        "id": c.config.id,
                        "model_id": c.config.model_id,
                        "stages": [s.value for s in c.config.stages],
                        "availability": c.status,
                        "selectable": c.selectable,
                        "digest": c.digest,
                    }
                    for c in choices
                ],
                "inference_verified": False,
                "admission": jobs.admission.status(),
                "verification_mode": verification_mode,
            }
        )

    @app.post("/api/v1/cases", status_code=201)
    def create_case(request: CreateCase) -> CreatedCase:
        case, version = workspace.create_case(request)
        return CreatedCase(case=case, version=version)

    @app.get("/api/v1/cases")
    def cases(
        outcome: Literal["callback_required", "no_callback", "needs_review"] | None = None,
        review: Literal["reviewed", "pending"] | None = None,
        status: Literal["running", "succeeded", "failed", "interrupted"] | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=50),
    ) -> list[CaseSummary]:
        return workspace.cases(
            outcome=outcome, review=review, status=status, offset=offset, limit=limit
        )

    @app.get("/api/v1/development-cases")
    def development_cases() -> list[DevelopmentSummary]:
        return [DevelopmentSummary(id=c.id, title=c.title) for c in DEVELOPMENT_CASES]

    @app.post("/api/v1/development-cases/{development_id}/load", status_code=201)
    def load_development_case(development_id: str, request: EmptyRequest) -> CreatedCase:
        choices = [c for c in DEVELOPMENT_CASES if c.id == development_id]
        if not choices:
            raise WorkspaceError("not_found", 404, "Choose a listed fictional development case.")
        selected = choices[0]
        case, version = workspace.create_case(
            CreateCase(text=selected.text, title=selected.title),
            "fictional_development",
            selected.id,
        )
        return CreatedCase(case=case, version=version)

    @app.get("/api/v1/cases/{case_id}")
    def case_detail(case_id: str) -> CaseDetail:
        case = workspace.get("case", case_id, CaseRecord)
        return CaseDetail(
            case=case,
            versions=tuple(
                VersionSummary.model_validate(v.model_dump(exclude={"text"}))
                for v in workspace.list_records("version", VersionRecord, case_id)
            ),
            jobs=tuple(workspace.list_records("job", JobRecord, case_id)),
        )

    @app.post("/api/v1/cases/{case_id}/versions", status_code=201)
    def create_version(case_id: str, request: CreateVersion) -> VersionRecord:
        return workspace.create_version(case_id, request)

    @app.get("/api/v1/cases/{case_id}/versions/{version_id}")
    def version(case_id: str, version_id: str) -> VersionRecord:
        record = workspace.get("version", version_id, VersionRecord)
        if record.case_id != case_id:
            raise WorkspaceError(
                "not_found", 404, "This version does not belong to the requested case."
            )
        return record

    @app.post("/api/v1/jobs", status_code=202)
    def submit(
        request: SubmitJob,
        idempotency_key: str = Header(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9-]+$"),
    ) -> JobRecord:
        return jobs.submit(idempotency_key, request)

    @app.get("/api/v1/jobs")
    def job_history(
        offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=50)
    ) -> list[JobRecord]:
        return workspace.list_records("job", JobRecord, offset=offset, limit=limit)

    @app.get("/api/v1/submissions/{key}")
    def submission(key: str) -> JobRecord:
        return workspace.submitted_job(key)

    @app.get("/api/v1/jobs/{job_id}")
    def job(job_id: str) -> JobRecord:
        return workspace.get("job", job_id, JobRecord)

    @app.get("/api/v1/cases/{case_id}/runs")
    def runs(
        case_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=50)
    ) -> list[JobRecord]:
        workspace.get("case", case_id, CaseRecord)
        rows = workspace.list_records("job", JobRecord, case_id, offset=offset, limit=limit)
        return rows

    @app.get("/api/v1/runs/{run_id}", response_model=RunSuccessRecord | RunFailureRecord)
    def run(run_id: str) -> JSONResponse:
        return JSONResponse(workspace.run(run_id))

    @app.post("/api/v1/runs/{run_id}/reviews", status_code=201)
    def review(
        run_id: str,
        request: CreateReview,
        idempotency_key: str = Header(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9-]+$"),
    ) -> ReviewRecord:
        return workspace.create_review(run_id, idempotency_key, request)

    @app.get("/api/v1/runs/{run_id}/reviews")
    def run_reviews(
        run_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=50)
    ) -> list[ReviewRecord]:
        return workspace.run_reviews(run_id, offset, limit)

    @app.get("/api/v1/cases/{case_id}/reviews")
    def reviews(
        case_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=50)
    ) -> list[ReviewRecord]:
        workspace.get("case", case_id, CaseRecord)
        return workspace.list_records("review", ReviewRecord, case_id, offset=offset, limit=limit)

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000, workers=1)


if __name__ == "__main__":
    main()
