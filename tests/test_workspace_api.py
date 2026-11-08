"""Real ASGI routes and persistence with a counted synthetic classifier; no model calls."""

import asyncio
import json
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from voice_callback.admission import InferenceAdmission
from voice_callback.api import create_app
from voice_callback.classify import POLICY_SHA256
from voice_callback.cli import main
from voice_callback.contracts import ModelEntry
from voice_callback.domain import (
    CallbackDecision,
    Failure,
    FailureCode,
    Outcome,
    RunFailure,
    RunProvenance,
    RunSuccess,
    Stage,
)
from voice_callback.jobs import JobService
from voice_callback.models import load_registry
from voice_callback.storage import render_json
from voice_callback.workspace import Workspace, WorkspaceError
from voice_callback.workspace_contracts import CreateCase, JobRecord, SubmitJob

ROOT = Path(__file__).resolve().parents[1]
MODEL = load_registry(ROOT / "config/models.json")[0]
TEXT = "Caller: Please call me back."


def synthetic(transcript, model, failure=None):
    provenance = RunProvenance(
        str(uuid4()),
        Stage.CLASSIFICATION,
        model,
        "synthetic-digest",
        "test-runtime",
        transcript.version_id,
        transcript.text_sha256,
        "callback-text-v2",
        "a" * 64,
        "1.0",
        POLICY_SHA256,
        "2026-11-06T00:00:00+00:00",
        0.1,
        case_id=transcript.case_id,
        request_sha256="b" * 64,
    )
    if failure:
        return RunFailure(provenance, Failure(failure, "Synthetic processing failure."))
    return RunSuccess(
        provenance,
        CallbackDecision(
            Outcome.CALLBACK_REQUIRED,
            ("CB-002",),
            "The caller requests a callback.",
            (transcript.text,),
        ),
    )


class ApiBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".test-work")
        self.root = Path(self.tmp.name)
        self.started, self.release = threading.Event(), threading.Event()
        self.release.set()
        self.calls = 0
        self.failure = None

        def classify(transcript, model):
            self.calls += 1
            self.started.set()
            if not self.release.wait(5):
                raise RuntimeError("Synthetic worker did not release.")
            return synthetic(transcript, model, self.failure)

        self.app = create_app(
            self.root / "workspace.sqlite3",
            self.root / "admission",
            ROOT / "config/models.json",
            classifier=classify,
        )
        self.loop = asyncio.new_event_loop()
        self.lifespan = self.app.router.lifespan_context(self.app)
        self.loop.run_until_complete(self.lifespan.__aenter__())
        self.nonce = self.request("GET", "/api/v1/session")[1]["nonce"]

    def tearDown(self):
        self.release.set()
        self.loop.run_until_complete(self.lifespan.__aexit__(None, None, None))
        self.loop.close()
        self.tmp.cleanup()

    def request(self, method, path, data=None, *, key=None, headers=None, raw=None):
        body = raw if raw is not None else json.dumps(data or {}).encode()
        values = {"host": "127.0.0.1:8000"}
        if method == "POST":
            values.update(
                {
                    "origin": "http://127.0.0.1:8000",
                    "content-type": "application/json",
                    "x-workspace-nonce": getattr(self, "nonce", ""),
                }
            )
        if key:
            values["idempotency-key"] = key
        values.update(headers or {})
        sent = []

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            sent.append(message)

        async def drive() -> None:
            path_only, _, query = path.partition("?")
            scope = {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.4"},
                "method": method,
                "scheme": "http",
                "path": path_only,
                "raw_path": path_only.encode(),
                "query_string": query.encode(),
                "headers": [(k.encode(), v.encode()) for k, v in values.items()],
                "server": ("127.0.0.1", 8000),
                "client": ("127.0.0.1", 12345),
                "root_path": "",
                "http_version": "1.1",
            }
            await self.app(scope, receive, send)

        self.loop.run_until_complete(drive())
        status = next(m["status"] for m in sent if m["type"] == "http.response.start")
        content = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
        return status, json.loads(content)

    def create_case(self, text=TEXT):
        status, content = self.request("POST", "/api/v1/cases", {"text": text})
        self.assertEqual(status, 201)
        return content["case"], content["version"]

    def submit(self, case, version, key="job-one"):
        return self.request(
            "POST",
            "/api/v1/jobs",
            {
                "case_id": case["id"],
                "transcript_version_id": version["id"],
                "model_config_id": MODEL.id,
            },
            key=key,
        )

    def wait_job(self, job_id):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status, job = self.request("GET", f"/api/v1/jobs/{job_id}")
            self.assertEqual(status, 200)
            if job["status"] != "running":
                return job
            time.sleep(0.01)
        self.fail("Synthetic job did not finish.")

    def test_explicit_idempotent_submission_versions_runs_and_reviews_survive_reopen(self):
        case, v1 = self.create_case("Caller: Please call me back.\nUnicode: café \u2028 text")
        self.assertEqual(self.calls, 0)
        status, v2 = self.request(
            "POST",
            f"/api/v1/cases/{case['id']}/versions",
            {"parent_version_id": v1["id"], "text": TEXT},
        )
        self.assertEqual(status, 201)
        self.assertEqual(self.calls, 0)
        self.assertEqual(
            self.request(
                "POST",
                f"/api/v1/cases/{case['id']}/versions",
                {"parent_version_id": v1["id"], "text": "stale"},
            )[0],
            409,
        )
        self.assertEqual(
            self.request("GET", f"/api/v1/cases/{case['id']}/versions/{v1['id']}")[1]["text"],
            v1["text"],
        )
        status, job = self.submit(case, v2)
        self.assertEqual(status, 202)
        finished = self.wait_job(job["id"])
        self.assertEqual(finished["status"], "succeeded")
        self.assertEqual(self.submit(case, v2)[1]["id"], job["id"])
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.submit(case, v1)[0], 409)
        run_id = finished["run_id"]
        before = self.request("GET", f"/api/v1/runs/{run_id}")[1]
        status, review = self.request(
            "POST",
            f"/api/v1/runs/{run_id}/reviews",
            {"decision": "no_callback", "note": "Separate judgment."},
            key="review-one",
        )
        self.assertEqual(status, 201)
        self.assertEqual(
            self.request(
                "POST",
                f"/api/v1/runs/{run_id}/reviews",
                {"decision": "no_callback", "note": "Separate judgment."},
                key="review-one",
            )[1],
            review,
        )
        self.request(
            "POST", f"/api/v1/runs/{run_id}/reviews", {"decision": "needs_review"}, key="review-two"
        )
        self.assertEqual(len(self.request("GET", f"/api/v1/cases/{case['id']}/reviews")[1]), 2)
        self.assertEqual(self.request("GET", f"/api/v1/runs/{run_id}")[1], before)
        reopened = Workspace(self.root / "workspace.sqlite3")
        self.assertEqual(reopened.run(run_id), before)
        self.assertEqual(reopened.get("job", job["id"], JobRecord).model.id, MODEL.id)

    def test_reconnect_lookups_and_review_pagination_are_read_only(self):
        case, version = self.create_case()
        self.assertEqual(self.request("GET", "/api/v1/submissions/missing")[0], 404)
        _, job = self.submit(case, version, "reconnect-key")
        finished = self.wait_job(job["id"])
        self.assertEqual(self.request("GET", "/api/v1/submissions/reconnect-key")[1], finished)
        self.assertEqual(self.request("GET", "/api/v1/jobs?limit=1")[1], [finished])
        self.assertEqual(self.request("GET", "/api/v1/jobs?offset=1")[1], [])
        run_id = finished["run_id"]
        for index, decision in enumerate(("no_callback", "needs_review")):
            self.assertEqual(
                self.request(
                    "POST",
                    f"/api/v1/runs/{run_id}/reviews",
                    {"decision": decision},
                    key=f"correction-{index}",
                )[0],
                201,
            )
        path = f"/api/v1/runs/{run_id}/reviews"
        self.assertEqual(self.request("GET", path + "?limit=1")[1][0]["decision"], "needs_review")
        self.assertEqual(
            self.request("GET", path + "?offset=1&limit=1")[1][0]["decision"], "no_callback"
        )
        self.assertEqual(self.request("GET", path + "?offset=2")[1], [])
        self.assertEqual(self.request("GET", path + "?limit=51")[0], 422)
        self.assertEqual(self.calls, 1)

    def test_storage_failure_returns_safe_recoverable_error(self):
        with patch.object(
            Workspace, "create_case", side_effect=sqlite3.OperationalError("private")
        ):
            status, body = self.request("POST", "/api/v1/cases", {"text": TEXT})
        self.assertEqual(status, 503)
        self.assertEqual(body["error"]["code"], "storage_unavailable")
        self.assertNotIn("private", json.dumps(body))
        self.assertEqual(self.request("GET", "/api/v1/cases")[1], [])
        self.assertEqual(self.calls, 0)

    def test_busy_rejects_other_keys_and_cli_and_does_not_queue(self):
        case, version = self.create_case()
        self.release.clear()
        _, job = self.submit(case, version)
        self.assertTrue(self.started.wait(3))
        self.assertEqual(self.submit(case, version, "second")[0], 409)
        self.assertEqual(self.submit(case, version)[1]["id"], job["id"])
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from voice_callback.admission import InferenceAdmission; from pathlib import Path; "
                f"InferenceAdmission(Path({str(self.root / 'admission')!r})).acquire()",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Another local inference operation", result.stderr)
        source = self.root / "input.txt"
        source.write_text(TEXT, encoding="utf-8")
        for command, arguments in [
            ("classify", ["--input", str(source), "--case-id", "synthetic"]),
            ("evaluate", ["--dataset", str(self.root / "not-a-dataset"), "--split", "development"]),
        ]:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "voice_callback.cli",
                    command,
                    "--model",
                    MODEL.id,
                    "--registry",
                    str(ROOT / "config/models.json"),
                    "--inference-lock-dir",
                    str(self.root / "admission"),
                    *arguments,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["failure"]["code"], "job_busy")
        self.release.set()
        self.wait_job(job["id"])
        self.assertEqual(self.calls, 1)

    def test_failures_have_no_output_and_do_not_replace_prior_success(self):
        case, version = self.create_case()
        _, job = self.submit(case, version)
        first = self.wait_job(job["id"])
        original = self.request("GET", f"/api/v1/runs/{first['run_id']}")[1]
        for code in [
            FailureCode.TIMEOUT,
            FailureCode.INVALID_OUTPUT,
            FailureCode.UNAVAILABLE,
            FailureCode.GPU_MEMORY,
        ]:
            self.failure = code
            _, job = self.submit(case, version, str(uuid4()))
            failed = self.wait_job(job["id"])
            self.assertEqual(failed["status"], "failed")
            result = self.request("GET", f"/api/v1/runs/{failed['run_id']}")[1]
            self.assertNotIn("output", result["run"])
            if code in {FailureCode.TIMEOUT, FailureCode.UNAVAILABLE}:
                self.assertEqual(failed["error"], "recovery_required")
                deadline = time.monotonic() + 3
                while (
                    not InferenceAdmission(self.root / "admission").stale()
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.01)
                self.assertEqual(self.submit(case, version, str(uuid4()))[0], 503)
                InferenceAdmission(self.root / "admission").recover()
            self.assertEqual(
                self.request(
                    "POST",
                    f"/api/v1/runs/{failed['run_id']}/reviews",
                    {"decision": "no_callback"},
                    key="bad-review",
                )[0],
                409,
            )
        self.assertEqual(self.request("GET", f"/api/v1/runs/{first['run_id']}")[1], original)

    def test_boundaries_reject_unsafe_input_without_echo_or_inference(self):
        for data in [
            {"text": ""},
            {"text": "é" * 6001},
            {"text": TEXT, "gold_label": "secret"},
            {"text": 7},
        ]:
            status, body = self.request("POST", "/api/v1/cases", data)
            self.assertEqual(status, 422)
            self.assertNotIn("secret", json.dumps(body))
        for headers in [
            {"host": "attacker.example"},
            {"origin": "https://attacker.example"},
            {"x-workspace-nonce": "wrong"},
            {"x-workspace-nonce": "é"},
        ]:
            self.assertEqual(
                self.request("POST", "/api/v1/cases", {"text": TEXT}, headers=headers)[0], 403
            )
        self.assertEqual(
            self.request("POST", "/api/v1/cases", raw=b'{"text":"one","text":"two"}')[0], 400
        )
        self.assertEqual(self.request("POST", "/api/v1/cases", raw=b"x" * 65537)[0], 413)
        self.assertEqual(self.request("GET", "/api/v1/cases?limit=51")[0], 422)
        self.assertEqual(self.calls, 0)

    def test_crash_marker_blocks_until_explicit_recovery(self):
        path = self.root / "separate-admission"
        admission = InferenceAdmission(path)
        lease = admission.acquire()
        lease.close()  # OS ownership ends while interrupted marker remains.
        self.assertTrue(admission.stale())
        with self.assertRaises(WorkspaceError) as failure:
            admission.acquire()
        self.assertEqual(failure.exception.code, "recovery_required")
        admission.recover()
        with admission.operation():
            pass
        self.assertFalse(admission.stale())

    def test_restart_reconciles_jobs_even_if_operator_recovered_marker_first(self):
        for recover_first in [False, True]:
            directory = self.root / str(recover_first)
            store = Workspace(directory / "store.sqlite3")
            case, version = store.create_case(CreateCase(text=TEXT))
            request = SubmitJob(
                case_id=case.id, transcript_version_id=version.id, model_config_id=MODEL.id
            )
            job = store.create_job(
                "orphan",
                request,
                ModelEntry.model_validate_json(render_json(MODEL)),
                {"source_sha256": "a" * 64, "git_revision": None, "working_tree_clean": False},
            )
            admission = InferenceAdmission(directory / "admission")
            admission.acquire().close()
            if recover_first:
                admission.recover()
            service = JobService(store, admission, (MODEL,), synthetic)
            try:
                recovered = store.get("job", job.id, JobRecord)
                self.assertEqual(recovered.status, "interrupted")
                self.assertIsNone(recovered.run_id)
            finally:
                service.close()

    def test_startup_during_cli_defers_recovery_until_ownership_is_free(self):
        for replay_orphan in (False, True):
            directory = self.root / f"deferred-{replay_orphan}"
            store = Workspace(directory / "store.sqlite3")
            case, version = store.create_case(CreateCase(text=TEXT))
            request = SubmitJob(
                case_id=case.id, transcript_version_id=version.id, model_config_id=MODEL.id
            )
            orphan = store.create_job(
                "orphan",
                request,
                ModelEntry.model_validate_json(render_json(MODEL)),
                {"source_sha256": "a" * 64, "git_revision": None, "working_tree_clean": False},
            )
            admission = InferenceAdmission(directory / "admission")
            admission.acquire().close()
            admission.recover()
            cli_lease = admission.acquire()
            service = JobService(store, admission, (MODEL,), synthetic)
            try:
                service.reconcile()
                self.assertEqual(store.get("job", orphan.id, JobRecord).status, "running")
                cli_lease.close(completed=True)
                accepted = service.submit("orphan" if replay_orphan else "new-job", request)
                service.close()
                self.assertEqual(store.get("job", orphan.id, JobRecord).status, "interrupted")
                expected = "interrupted" if replay_orphan else "succeeded"
                self.assertEqual(store.get("job", accepted.id, JobRecord).status, expected)
                self.assertEqual(admission.status(), "ready")
            finally:
                if not cli_lease.stream.closed:
                    cli_lease.close(completed=True)
                service.close()

    def test_development_inputs_and_filters_never_invoke_inference(self):
        status, examples = self.request("GET", "/api/v1/development-cases")
        self.assertEqual(status, 200)
        self.assertEqual(len(examples), 3)
        self.assertNotIn("label", json.dumps(examples))
        _, loaded = self.request("POST", "/api/v1/development-cases/demo-101/load", {})
        self.assertEqual(loaded["version"]["origin"], "fictional_development")
        self.assertEqual(loaded["version"]["development_case_id"], "demo-101")
        self.assertEqual(
            self.request("POST", "/api/v1/development-cases/held-out/load", {})[0], 404
        )
        self.assertEqual(self.calls, 0)
        self.assertEqual(len(self.request("GET", "/api/v1/cases?review=pending")[1]), 1)
        self.assertEqual(self.request("GET", "/api/v1/cases?outcome=callback_required")[1], [])
        _, job = self.submit(loaded["case"], loaded["version"])
        finished = self.wait_job(job["id"])
        self.assertEqual(len(self.request("GET", "/api/v1/cases?outcome=callback_required")[1]), 1)
        self.request(
            "POST",
            f"/api/v1/runs/{finished['run_id']}/reviews",
            {"decision": "no_callback"},
            key="filter-review",
        )
        self.assertEqual(len(self.request("GET", "/api/v1/cases?review=reviewed")[1]), 1)
        self.assertEqual(self.request("GET", "/api/v1/cases?review=pending")[1], [])
        self.assertEqual(self.calls, 1)

    def test_cli_transport_timeout_preserves_recovery_admission(self):
        directory = self.root / "cli-timeout"
        directory.mkdir()
        source = directory / "input.txt"
        source.write_text(TEXT, encoding="utf-8")

        def timeout(transcript, model, client, **kwargs):
            return synthetic(transcript, model, FailureCode.TIMEOUT)

        with (
            patch("voice_callback.cli.classify", side_effect=timeout),
            redirect_stdout(StringIO()),
            redirect_stderr(StringIO()),
        ):
            result = main(
                [
                    "classify",
                    "--model",
                    MODEL.id,
                    "--input",
                    str(source),
                    "--case-id",
                    "synthetic",
                    "--registry",
                    str(ROOT / "config/models.json"),
                    "--output-dir",
                    str(directory / "runs"),
                    "--inference-lock-dir",
                    str(directory / "admission"),
                ]
            )
        self.assertEqual(result, 1)
        self.assertTrue(InferenceAdmission(directory / "admission").stale())
        self.assertEqual(len(list((directory / "runs").glob("*.json"))), 1)

    def test_terminal_storage_outage_is_reconciled_after_storage_returns(self):
        directory = self.root / "storage-outage"
        store = Workspace(directory / "workspace.sqlite3")
        case, version = store.create_case(CreateCase(text=TEXT))
        admission = InferenceAdmission(directory / "admission")
        service = JobService(store, admission, (MODEL,), synthetic)
        try:
            with (
                patch.object(
                    store, "complete_job", side_effect=sqlite3.OperationalError("disk full")
                ),
                patch.object(
                    store, "interrupt_jobs", side_effect=sqlite3.OperationalError("disk full")
                ),
            ):
                job = service.submit(
                    "outage",
                    SubmitJob(
                        case_id=case.id,
                        transcript_version_id=version.id,
                        model_config_id=MODEL.id,
                    ),
                )
                service.close()
            self.assertEqual(store.get("job", job.id, JobRecord).status, "running")
            service.reconcile()
            self.assertEqual(store.get("job", job.id, JobRecord).status, "interrupted")
            self.assertEqual(admission.status(), "recovery_required")
            admission.recover()
            service.reconcile()
            self.assertEqual(admission.status(), "ready")
        finally:
            service.close()

    def test_unexpected_worker_failure_is_visible_and_requires_recovery(self):
        # Exercise the service directly with a failing provider, using isolated storage.
        directory = self.root / "worker-crash"
        store = Workspace(directory / "workspace.sqlite3")
        created, saved = store.create_case(CreateCase(text=TEXT))

        def crash(transcript, model):
            raise RuntimeError("UNTRUSTED_PROVIDER_DETAIL")

        admission = InferenceAdmission(directory / "admission")
        service = JobService(store, admission, (MODEL,), crash)
        try:
            request = SubmitJob(
                case_id=created.id, transcript_version_id=saved.id, model_config_id=MODEL.id
            )
            job = service.submit("crash-job", request)
            current = store.get("job", job.id, JobRecord)
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                current = store.get("job", job.id, JobRecord)
                if current.status == "interrupted":
                    break
                time.sleep(0.01)
            self.assertEqual(current.status, "interrupted")
            self.assertIsNone(current.run_id)
            self.assertNotIn("UNTRUSTED", current.model_dump_json())
        finally:
            service.close()
        self.assertTrue(admission.stale())
        with self.assertRaises(WorkspaceError):
            service.submit("next-job", request)
        with closing(sqlite3.connect(directory / "workspace.sqlite3")) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE records SET document='{}' WHERE kind='version'")


if __name__ == "__main__":
    unittest.main()
