"""Transactional local case/version, job, immutable run and review storage."""

import json
import sqlite3
from collections.abc import Generator
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import TypeVar
from uuid import uuid4

from .classify import validate_decision
from .contracts import RUN_RECORD, Contract, ModelEntry, validate_record
from .domain import CallbackDecision, JsonValue, RunResult, RunSuccess
from .evaluation_contracts import SourceIdentity
from .json_io import parse_json
from .storage import render_json, render_run
from .workspace_contracts import (
    CaseRecord,
    CaseSummary,
    CreateCase,
    CreateReview,
    CreateVersion,
    JobRecord,
    ReviewRecord,
    SubmitJob,
    VersionRecord,
)

Record = TypeVar("Record", bound=Contract)


class WorkspaceError(Exception):
    def __init__(self, code: str, status: int, message: str):
        self.code, self.status, self.message = code, status, message
        super().__init__(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def identifier() -> str:
    return str(uuid4())


class Workspace:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.transaction() as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in (0, 1):
                raise WorkspaceError(
                    "storage_version", 503, "This workspace needs a compatible application version."
                )
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records (
                    kind TEXT NOT NULL, id TEXT NOT NULL, case_id TEXT NOT NULL,
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT, document TEXT NOT NULL,
                    UNIQUE(kind, id)
                );
                CREATE INDEX IF NOT EXISTS case_records ON records(kind, case_id, sequence);
                CREATE TABLE IF NOT EXISTS requests (
                    scope TEXT NOT NULL, key TEXT NOT NULL, payload TEXT NOT NULL,
                    resource_id TEXT NOT NULL, PRIMARY KEY(scope, key)
                );
                CREATE TRIGGER IF NOT EXISTS immutable_records_update BEFORE UPDATE ON records
                WHEN OLD.kind IN ('version','run','review')
                BEGIN SELECT RAISE(ABORT,'Immutable workspace record'); END;
                CREATE TRIGGER IF NOT EXISTS immutable_records_delete BEFORE DELETE ON records
                BEGIN SELECT RAISE(ABORT,'Workspace history cannot be deleted'); END;
                CREATE TRIGGER IF NOT EXISTS terminal_job_update BEFORE UPDATE ON records
                WHEN OLD.kind='job' AND json_extract(OLD.document,'$.status')!='running'
                BEGIN SELECT RAISE(ABORT,'Terminal job is immutable'); END;
                PRAGMA user_version=1;
            """)

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        with closing(sqlite3.connect(self.path, timeout=5)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            yield db

    @staticmethod
    def _insert(db: sqlite3.Connection, kind: str, case_id: str, record: Contract) -> None:
        record_id = record.model_dump()["id"]
        db.execute(
            "INSERT INTO records(kind,id,case_id,document) VALUES (?,?,?,?)",
            (kind, record_id, case_id, record.model_dump_json()),
        )

    @staticmethod
    def _get(db: sqlite3.Connection, kind: str, record_id: str, model: type[Record]) -> Record:
        row = db.execute(
            "SELECT document FROM records WHERE kind=? AND id=?", (kind, record_id)
        ).fetchone()
        if row is None:
            raise WorkspaceError("not_found", 404, "The requested workspace record does not exist.")
        return model.model_validate_json(row[0])

    def get(self, kind: str, record_id: str, model: type[Record]) -> Record:
        with self.transaction() as db:
            return self._get(db, kind, record_id, model)

    def list_records(
        self,
        kind: str,
        model: type[Record],
        case_id: str | None = None,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Record]:
        with self.transaction() as db:
            rows = db.execute(
                "SELECT document FROM records WHERE kind=? AND (? IS NULL OR case_id=?) "
                "ORDER BY sequence DESC LIMIT ? OFFSET ?",
                (kind, case_id, case_id, limit, offset),
            ).fetchall()
            return [model.model_validate_json(row[0]) for row in rows]

    def create_case(
        self, request: CreateCase, origin: str = "pasted", development_id: str | None = None
    ) -> tuple[CaseRecord, VersionRecord]:
        case_id, version_id, created = identifier(), identifier(), now()
        case = CaseRecord(
            id=case_id, title=request.title, created_at=created, current_version_id=version_id
        )
        version = VersionRecord.model_validate(
            {
                "id": version_id,
                "case_id": case_id,
                "parent_version_id": None,
                "text": request.text,
                "text_sha256": sha256(request.text.encode()).hexdigest(),
                "origin": origin,
                "development_case_id": development_id,
                "created_at": created,
            }
        )
        with self.transaction() as db:
            self._insert(db, "case", case_id, case)
            self._insert(db, "version", case_id, version)
        return case, version

    def cases(
        self,
        *,
        outcome: str | None = None,
        review: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[CaseSummary]:
        with self.transaction() as db:
            rows = db.execute(
                """
                SELECT c.document,j.document,r.document,rv.id FROM records c
                LEFT JOIN records j ON j.sequence=(SELECT MAX(sequence) FROM records
                    WHERE kind='job' AND case_id=c.id)
                LEFT JOIN records r ON r.kind='run' AND r.id=json_extract(j.document,'$.run_id')
                LEFT JOIN records rv ON rv.sequence=(SELECT MAX(sequence) FROM records
                    WHERE kind='review' AND case_id=c.id
                    AND json_extract(document,'$.run_id')=json_extract(j.document,'$.run_id'))
                WHERE c.kind='case'
                AND (? IS NULL OR json_extract(r.document,'$.run.output.label')=?)
                AND (? IS NULL OR json_extract(j.document,'$.status')=?)
                AND (? IS NULL OR (?='reviewed' AND rv.id IS NOT NULL)
                     OR (?='pending' AND rv.id IS NULL))
                ORDER BY c.sequence DESC LIMIT ? OFFSET ?
            """,
                (outcome, outcome, status, status, review, review, review, limit, offset),
            ).fetchall()
            result: list[CaseSummary] = []
            for case_json, job_json, run_json, review_id in rows:
                case = CaseRecord.model_validate_json(case_json)
                job = JobRecord.model_validate_json(job_json) if job_json else None
                record = json.loads(run_json) if run_json else None
                result.append(
                    CaseSummary.model_validate(
                        {
                            **case.model_dump(),
                            "latest_job_id": job.id if job else None,
                            "processing_status": job.status if job else None,
                            "outcome": record["run"]["output"]["label"]
                            if record and record["status"] == "success"
                            else None,
                            "human_reviewed": review_id is not None,
                        }
                    )
                )
            return result

    def create_version(self, case_id: str, request: CreateVersion) -> VersionRecord:
        with self.transaction() as db:
            case = self._get(db, "case", case_id, CaseRecord)
            if case.current_version_id != request.parent_version_id:
                raise WorkspaceError(
                    "stale_version", 409, "Reload the case before saving this edit."
                )
            parent = self._get(db, "version", request.parent_version_id, VersionRecord)
            if parent.text == request.text:
                return parent
            version = VersionRecord(
                id=identifier(),
                case_id=case_id,
                parent_version_id=parent.id,
                text=request.text,
                text_sha256=sha256(request.text.encode()).hexdigest(),
                origin="correction",
                created_at=now(),
            )
            self._insert(db, "version", case_id, version)
            updated = case.model_copy(update={"current_version_id": version.id})
            db.execute(
                "UPDATE records SET document=? WHERE kind='case' AND id=?",
                (updated.model_dump_json(), case_id),
            )
        return version

    @staticmethod
    def _previous(db: sqlite3.Connection, scope: str, key: str, payload: str) -> str | None:
        row = db.execute(
            "SELECT payload,resource_id FROM requests WHERE scope=? AND key=?", (scope, key)
        ).fetchone()
        if row is None:
            return None
        if row[0] != payload:
            raise WorkspaceError(
                "idempotency_conflict", 409, "Use a new submission key for different input."
            )
        return str(row[1])

    def submitted_job(self, key: str) -> JobRecord:
        with self.transaction() as db:
            row = db.execute(
                "SELECT resource_id FROM requests WHERE scope='job' AND key=?", (key,)
            ).fetchone()
            if row is None:
                raise WorkspaceError(
                    "not_found", 404, "No accepted submission was found for this key."
                )
            return self._get(db, "job", row[0], JobRecord)

    def previous_job(self, key: str, request: SubmitJob) -> JobRecord | None:
        with self.transaction() as db:
            previous = self._previous(db, "job", key, request.model_dump_json())
            return self._get(db, "job", previous, JobRecord) if previous else None

    def create_job(
        self, key: str, request: SubmitJob, model: ModelEntry, source: dict[str, JsonValue]
    ) -> JobRecord:
        with self.transaction() as db:
            case = self._get(db, "case", request.case_id, CaseRecord)
            version = self._get(db, "version", request.transcript_version_id, VersionRecord)
            if version.case_id != case.id:
                raise WorkspaceError(
                    "invalid_version", 422, "Choose a version belonging to this case."
                )
            job = JobRecord(
                id=identifier(),
                case_id=case.id,
                transcript_version_id=version.id,
                model=model,
                source=SourceIdentity.model_validate(source),
                status="running",
                created_at=now(),
            )
            self._insert(db, "job", case.id, job)
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?)",
                ("job", key, request.model_dump_json(), job.id),
            )
        return job

    def complete_job(
        self, job_id: str, result: RunResult, *, recovery_required: bool = False
    ) -> None:
        content = render_run(result)
        status = "succeeded" if json.loads(content)["status"] == "success" else "failed"
        with self.transaction() as db:
            job = self._get(db, "job", job_id, JobRecord)
            if job.status != "running":
                raise WorkspaceError(
                    "job_completed", 409, "This job already has a terminal result."
                )
            version = self._get(db, "version", job.transcript_version_id, VersionRecord)
            if (
                result.provenance.transcript_sha256 != version.text_sha256
                or result.provenance.transcript_version_id != version.id
                or result.provenance.case_id != job.case_id
                or ModelEntry.model_validate_json(render_json(result.provenance.model)) != job.model
            ):
                raise ValueError("Result does not match its admitted transcript.")
            if isinstance(result, RunSuccess):
                if not isinstance(result.output, CallbackDecision):
                    raise ValueError("Workspace requires a classification result.")
                validate_decision(render_json(result.output), version.text)
            db.execute(
                "INSERT INTO records(kind,id,case_id,document) VALUES ('run',?,?,?)",
                (result.provenance.run_id, job.case_id, content),
            )
            updated = job.model_copy(
                update={
                    "status": status,
                    "run_id": result.provenance.run_id,
                    "finished_at": now(),
                    "error": "recovery_required" if recovery_required else None,
                }
            )
            db.execute(
                "UPDATE records SET document=? WHERE kind='job' AND id=?",
                (updated.model_dump_json(), job_id),
            )

    def interrupt_jobs(self) -> None:
        with self.transaction() as db:
            for record_id, content in db.execute(
                "SELECT id,document FROM records WHERE kind='job'"
            ).fetchall():
                job = JobRecord.model_validate_json(content)
                if job.status == "running":
                    job = job.model_copy(
                        update={
                            "status": "interrupted",
                            "error": "recovery_required",
                            "finished_at": now(),
                        }
                    )
                    db.execute(
                        "UPDATE records SET document=? WHERE kind='job' AND id=?",
                        (job.model_dump_json(), record_id),
                    )

    def run(self, run_id: str) -> dict[str, JsonValue]:
        with self.transaction() as db:
            row = db.execute(
                "SELECT document FROM records WHERE kind='run' AND id=?", (run_id,)
            ).fetchone()
            if row is None:
                raise WorkspaceError("not_found", 404, "The requested run does not exist.")
            value = parse_json(row[0])
            validate_record(RUN_RECORD, value)
            if not isinstance(value, dict):
                raise ValueError("Invalid stored run.")
            return value

    def create_review(self, run_id: str, key: str, request: CreateReview) -> ReviewRecord:
        record = self.run(run_id)
        if record["status"] != "success":
            raise WorkspaceError(
                "no_model_output", 409, "A processing failure has no recommendation to review."
            )
        with self.transaction() as db:
            row = db.execute(
                "SELECT case_id FROM records WHERE kind='run' AND id=?", (run_id,)
            ).fetchone()
            assert row is not None
            case_id = str(row[0])
            payload = request.model_dump_json()
            previous = self._previous(db, f"review:{run_id}", key, payload)
            if previous:
                return self._get(db, "review", previous, ReviewRecord)
            job_row = db.execute(
                "SELECT document FROM records WHERE kind='job' AND case_id=? "
                "AND json_extract(document,'$.run_id')=?",
                (case_id, run_id),
            ).fetchone()
            assert job_row is not None
            job = JobRecord.model_validate_json(job_row[0])
            review = ReviewRecord(
                id=identifier(),
                run_id=run_id,
                transcript_version_id=job.transcript_version_id,
                decision=request.decision,
                note=request.note,
                created_at=now(),
            )
            self._insert(db, "review", case_id, review)
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?)",
                (f"review:{run_id}", key, payload, review.id),
            )
        return review

    def run_reviews(self, run_id: str, offset: int = 0, limit: int = 50) -> list[ReviewRecord]:
        self.run(run_id)
        with self.transaction() as db:
            rows = db.execute(
                "SELECT document FROM records WHERE kind='review' "
                "AND json_extract(document,'$.run_id')=? ORDER BY sequence DESC "
                "LIMIT ? OFFSET ?",
                (run_id, limit, offset),
            ).fetchall()
            return [ReviewRecord.model_validate_json(row[0]) for row in rows]
