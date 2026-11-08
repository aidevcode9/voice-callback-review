# F-008: Review desk reliability corrections

Owner: project owner. Status: functional corrections verified, 2026-11-07; commit/PR handoff follows exact snapshot gates.
Branch: codex/f-006-review-desk, retained as requested.
Dependencies: completed F-006 and F-007; this is a bounded correction batch, not a new visual design.
Source: owner requested fixes for all six committed-review findings, followed by a commit and a PR for review. Merge and deployment are excluded.

## Workflow and requirements

project-workflow orchestrates; house systematic-debugging leads the already reproduced failures. Compared pstack blast-radius's wider investigation approach; the six concrete reproductions provide the needed root-cause evidence without another architecture arena. TDD supports cheap regression targets. Code-review-workflow supports an independent check after correction; branch-finish and the configured snapshot gates govern publication.

| Acceptance | Observable correction |
| --- | --- |
| F-008-AC01 | A timed-out evaluation retains recovery admission even when provenance validation rejects configuration drift. No next request or answer read. |
| F-008-AC02 | A worker whose terminal storage writes fail becomes interrupted after storage returns and read/submission reconciliation retries. A live inference owner is never interrupted. |
| F-008-AC03 | A failed second stack launch cannot signal another launch's Nginx. Each invocation owns its PID/log paths and stops only its children. |
| F-008-AC04 | Text cannot be lost by editing during a pending transcript save. |
| F-008-AC05 | Completion of a tracked job is reconciled even if another job is already running at the next poll. |
| F-008-AC06 | Reconnect preserves the current editor rather than restoring an unrelated abandoned new-case draft. |
| F-008-AC07 | Local .archify/, .ua/ and generated verification PNGs stay ignored and absent from the published PR tree/history. |

## Approach and reproduction evidence

The committed review against c82f0ed..06966e1 reproduced all six defects. Synthetic CLI/runtime and temporary SQLite repros established the admission/storage failures; an isolated process-boundary repro established shared-PID shutdown; a production Next.js page with fictional API responses established all three UI races. No live model or owner database was used. Preserve this evidence as regression behavior in existing test tooling.

Expose inference-result observation to the evaluation caller that owns the lease, before persistence/provenance checks can fail. Mark deferred reconciliation pending after failed worker publication. Separate each launch's Nginx workspace structurally. Disable transcript editing during a save, separate initial draft restoration from reconnect, and reconcile the prior tracked job independently of the new active job. Keep exact prompt content, schema, accepted policy, stored review history and frozen datasets unchanged.

## Plan and checks

- [x] Add focused regressions and confirm failing-before behavior.
- [x] Correct the six owning boundaries and rerun the regression checks.
- [x] Run Python quality/behavior, actual browser regressions and documentation checks.
- [x] Independently review the corrections and update living docs.
- Required branch handoff: pass exact staged and committed snapshot gates, commit fixes, publish clean codex/f-006-review-desk-pr against verified main, and create the PR. Do not merge.

Pre-implementation quality-baseline configuration passed. Tests and final outcomes are recorded below after execution. The owner's running desk and local database are left alone. Unavailable hosted checks remain explicit. Completion, owner acceptance, merge and deployment are separate states.

## Observed verification and review

| Criterion | Failing-before evidence | Passing-after evidence |
| --- | --- | --- |
| AC01 | CLI drift+timeout test observed admission ready after one timed-out request. | New CLI regression retains recovery_required, the saved timeout and aborted declaration; no next request or answer read. |
| AC02 | Storage-outage test left the durable job running after storage returned and reconcile ran. | New test marks it interrupted after both publication writes fail and storage returns; pending admission stays conservative until explicit recovery. |
| AC03 | Process-boundary test observed quit against an existing shared PID without this launch starting Nginx. | New test verifies no signal to the existing PID, unchanged old PID file and termination of this invocation's child. Actual stack browser checks also use the private launch prefix. |
| AC04 | Pending-save browser regression found the textarea still enabled. | Rebuilt production UI disables it during the transaction and preserves the exact submitted text. |
| AC05 | A terminal result was not displayed when B had become active between polls. | New production-page regression displays A's successful result/history while B runs and retains it when B ends. |
| AC06 | After a subsequent observable runtime poll, reconnect had replaced case A's edit with the old new-case draft. | New production-page regression retains case A's heading and current edit across reconnect. |
| AC07 | Earlier local commits contained 30 generated PNGs; .archify/.ua were untracked. | Local files are preserved, generated PNGs removed from the index, ignore rules verified. Clean publication commit will use the final tree with main as its sole parent, preserving original local commits without pushing their PNG ancestry. |

The full Python suite passed 120 tests; all five production browser flows passed. Three flows use fictional intercepted API responses for deterministic state ordering, and the original two drive actual Nginx/FastAPI/SQLite with a controlled Ollama HTTP fixture. Both static prototype directions passed their verification script after the comparison page was made independent of PNGs. Ruff/format/Pyright and 235 local documentation links/OpenAPI/lifecycle checks passed before final snapshot validation.

Fresh independent frontend review scored all three findings resolved, found no introduced actionable bug, and ran TypeScript/Biome. Fresh bounded backend/process review scored its three findings resolved by code/test inspection; execution evidence is the primary failing-before/passing-after checks. An earlier reviewer hit a usage limit after its CLI test passed and its Windows ASGI setup stalled; only that review's verified unittest processes were stopped. No independent full-suite claim is made. Bounded-list job fallback and preservation of a different follow ID were inspected but have no dedicated extra regression beyond the relevant flow.

Implementation and verification are complete. Final snapshot results and local/publication commit identities are recorded in the completing commit/PR. Main was fetched and verified at c82f0ed; the repository default branch is main and no existing open PR was found. Original local commits remain on codex/f-006-review-desk. The publication branch is a single equivalent-tree commit over main, created in an isolated worktree so the running owner's source files are not temporarily switched to the old base. No model inference, frozen-artifact changes, merge or deployment occurs in this batch. Hosted CI status is reported from the PR, not inferred from local checks.

## PR publication and hosted restart check

PR #3 publishes codex/f-006-review-desk-pr, initially at 135f092. The original local branch retains 0b1c1e4 and its unpublished predecessors. Both exact snapshot gates passed: 120 Python tests, five browser flows, quality/data/package checks and 233 snapshot documentation links. The published tree and new reachable history contain no PNGs, .archify/ or .ua/.

The first hosted run passed quality/data/docs and all three Python/package matrix jobs. Linux browser acceptance exposed a restart-test race: its status-only readiness poll accepted the old API's HTTP 200 before shutdown, then reloaded during the restart gap. An isolated fixture reproduction confirmed the first 200 still had the old nonce, followed by failed requests before the new instance became ready. The browser check now validates the session response and waits for a changed per-instance nonce before reloading. This keeps the persistence assertion tied to the restarted API rather than weakening it or increasing timeouts. The PR records the subsequent verification and hosted result.
