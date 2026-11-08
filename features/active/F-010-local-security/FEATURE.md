# F-010: Local desk and test fixture security

Owner: project owner. Dependencies: F-006. Selected workflow: planning-workflows for this bounded two-boundary change; project-workflow orchestration and testability support. Architect was considered; parallel design exploration is disproportionate to two established controls.

## Requirements

Prevent other origins from framing the local review desk and prevent unrelated browser origins from controlling the isolated browser-test runtime. Hosted security and protection from a malicious local process are excluded.

| Acceptance ID | Observable criterion |
| --- | --- |
| F-010-AC01 | Desk responses prohibit framing and a separate origin cannot load the desk in a frame. |
| F-010-AC02 | Fixture control rejects requests without its per-run secret while the harness can still control it. |

## Technical approach

Nginx supplies CSP frame-ancestors and X-Frame-Options on both locations, including errors. Playwright creates a random per-run secret inherited by the test stack and workers; the fixture requires it for control reads and writes. This is a test boundary, not authentication for production. The existing local runtime API remains unchanged.

## Implementation and verification

- [x] Verify browser behavior and project checks.
- [x] Review changes and update living documentation.

| Acceptance ID or project check | Scenario | Observed result |
| --- | --- | --- |
| F-010-AC01 | Real Nginx response headers and a separate loopback-origin frame in Playwright | Passed; desk heading did not load in the frame, and page/API responses carried both headers. |
| F-010-AC02 | Unauthenticated GET/POST and cross-origin form-compatible request, then authenticated control | Passed; control returned 403 and the mode remained unchanged; existing fixture-driven workflows passed. |
| Project checks | Shared quality, tests, data, docs, package and web suites | Passed across the initial run and separate web rerun with the existing offline npm cache; 120 Python and 6 browser tests passed. The initial all-in-one run was interrupted during web dependency installation. A Windows Uvicorn h11 warning occurred during the passing browser suite. |


## Current state and completion

Implementation and working-tree checks complete. Staged snapshot preflight is required for commit; results are reported at handoff. No merge or deployment. The branch starts from F-006 review desk commit 2be6a25 and is independent of concurrent Langfuse work.
