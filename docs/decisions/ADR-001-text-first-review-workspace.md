# ADR-001: Text-first review workspace and separate API

Date: 2026-11-06.
Status: architectural direction approved by owner under SRC-020; Review desk selected under SRC-021 and implemented/functionally verified under SRC-022. Model quality and deployment remain separate.

## Context

The existing Python classifier and evaluation core are implemented; both PR #1 and PR #2 are merged. The owner wants a precise text-review/testing workspace suitable for senior engineering review and explicitly rejected Streamlit. Audio integration is deferred to the end. A frontend/API boundary introduces distinct state, persistence and browser acceptance beyond F-004's model pipeline.

## Options

- Streamlit alongside the Python core: simpler initial setup, rejected by the owner for this workspace.
- Separate Next.js and Python API origins: flexible, but adds browser-origin/CORS complexity with no local-demo benefit.
- Next.js plus thin proposed FastAPI API behind Nginx: selected direction, one browser-facing origin and reuse of the existing classifier/contracts.

## Decision

Create substantial [F-006](../../features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) for the text frontend/API. Nginx routes pages/assets to proposed Next.js and /api to proposed Python/FastAPI. No production components are implemented in this design batch. [The API specification](../../features/completed/F-006-text-review-workspace/02_TECHNICAL_SPEC.md) proposes explicit idempotent submissions, one active local inference job, polling, bounded safe errors and append-only versions/reviews. No broker, distributed queue or cloud service is needed.

F-004 retains core evaluation, candidate-freeze/held-out controls, transcription and paired-audio verification. F-004-AC09 transfers to F-006-AC03/AC05; UI selectors have F-006 browser acceptance while stage availability and final audio selection remain F-004 responsibilities. Finish text review/testing before provisioning/integrating transcription and running paired audio.

## Consequences and superseded assumptions

The earlier Streamlit/app.py proposal and audio-before-dashboard order are superseded. Dated execution evidence remains historical. Frontend tooling and API/admission/recovery tests must be configured before production implementation. Held-out cases and answers are excluded from the workspace; expected-label evaluation remains separate. Human review never changes model output or gold. Hosting and quality acceptance remain open. Two interactive visual directions are rendered before owner selection; the agent recommends Review desk, with Casebook retained as a distinct alternative.

## Implementation update, 2026-11-07

The first backend slice uses embedded SQLite, not the earlier JSON-per-record proposal. Transactions couple admission metadata/idempotency and publish completed runs with terminal job state; immutable-history triggers protect versions, runs and review events. This adds no database service. A shared OS file lock and persistent interrupted-operation marker cover CLI/API admission; explicit operator recovery follows a stopped/restarted runtime. See the F-006 specification for actual contracts and remaining frontend/proxy checks.
