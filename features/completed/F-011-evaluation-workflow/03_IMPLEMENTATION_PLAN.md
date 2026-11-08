# F-011: Implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).

## Workflow and ownership

- Lead: `planning-workflows`, selected through `project-workflow` after reading the
  profile, workflow manager, house planning and pstack architect/arena candidates.
- Support: adapted architect competing-sketch step, code-quality, error-handling,
  focused behavior tests and verification-before-completion. Branch-finish and
  configured snapshot preflight apply to handoff.
- Available models do not include pstack's default Claude/Grok seats or a
  cross-family judge. Two independent parent-model sketches are used; root owns
  synthesis. No full architect/arena run is claimed.
- Branch: `codex/f-011-evaluation-workflow`, created and verified on 2026-11-08.
  It starts at 884168c, preserving all unpublished commits and working-tree edits.
- Prior edits: evaluation/Langfuse docs, F-009 plan, development launcher/tests and
  an unrelated local reviewer HTML. Preserve unrelated HTML. The related launcher
  work is carried into this feature rather than silently discarded.
- Sketch agents write separate ignored `.test-work/f011-design/candidate-a` and
  `candidate-b` folders. They do not edit shared source or read secrets/held-out data.

## Verifiable checkpoints

- [x] Create/verify feature branch; validate engineering gate configuration.
- [x] Define requirements, compare both sketches and record usage/interfaces.
- [x] Implement configuration, committed-source preparation and canonical command.
- [x] Implement immutable saved-run inspection, report and baseline comparison.
- [x] Integrate progress, interruption/recovery guidance and dated saved-run history.
- [x] Verify the actual canonical subprocess against a controlled HTTP fixture.
- [x] Inspect rendered reports on desktop/narrow in light and dark; fix mobile tables.
- [x] Run all working-tree shared gates and self-review; update living diagrams/docs.

Branch handoff additionally runs the configured staged snapshot before commit,
then committed snapshot and actual prepare-only command. Their local receipts
are `.test-work/f011-precommit.log` and `.test-work/f011-review.log`; the handoff
reports their outcome and exact committed revision.

## Acceptance and check evidence

| Acceptance ID or project check | Command or scenario | Observed result, 2026-11-08 |
| --- | --- | --- |
| Engineering configuration | `.venv\Scripts\python.exe scripts/check_quality_baseline.py` | Passed. |
| Feature branch | `git branch --show-current` | `codex/f-011-evaluation-workflow`, preserving starting history. |
| F-011-AC01 | `test_evaluation_integration.py` actual subprocess and `test_evaluation_workflow.py` disposable Git tests | Committed checkout/revision/source identity, shared lock/output routing, dirty-source refusal and checkout reuse verified. |
| F-011-AC02 | `test_evaluation_environment.py` and integration import sentinel | 14 environment cases passed; explicit --no-trace prevents SDK import despite inherited enabled settings. No credentials in output/model/config artifacts. |
| F-011-AC03 | `test_evaluate.py` persisted progress, interruption and timeout/admission scenarios | 26 evaluator cases passed as part of full suite. Progress observes flushed predictions; incomplete directory/marker retained without answers/report. |
| F-011-AC04 | `test_evaluation_review.py` and rendered browser acceptance | 14 reporting cases passed; reports expose metrics/counts/provenance/all cases with escaped data, undefined ratios and no inferred acceptance. |
| F-011-AC05 | Actual two-run integration plus saved-snapshot tests | Baseline D2 fix, no regression, null deltas, incompatible data/definitions rejection, different source/model compatibility and unchanged baseline bytes verified. |
| F-011-AC06 | Offline CLI/history and corrupt/incomplete/held-out read-boundary tests | No further HTTP calls for saved review; held-out declarations rejected before input/answer loading. Derived HTML is exclusive and content-versioned when it changes. |
| F-011-AC07 | Docs, current architecture/user flow, feature spec and evidence README | Working-tree docs gate verified 274 links before final lifecycle/evidence update; final snapshot gate rechecks all delivered links. |
| Shared project gates | `.venv\Scripts\python.exe scripts/check_project.py` with existing Chromium/Nginx paths | All suites passed: Ruff, format, strict types, 165 Python tests, frozen data, docs/OpenAPI, clean wheel and six production-stack browser tests. |
| Report browser verification | Local Playwright fixture, 1440/390 light/dark | Four viewport/theme combinations passed; screenshots inspected. Table wrapping fixed and local scrolling/focus/no-overflow/no-remote-assets/injection checks passed. See [evidence](../../../docs/evidence/F-011/README.md). |
| Staged/committed snapshot | `scripts/codex_preflight.py --mode pre-commit` then `--mode review` | Executed at the commit boundary; local receipts and final handoff report the result. |

## Review and design refinements

An independent read-only runner review reproduced private worker --prepare-only
being accepted but ignored. The worker now rejects parent-only flags before
execution and has a focused check. The full subprocess comparison test then caught
nested Pydantic ratios failing JSON serialization; the CLI uses the typed Pydantic
adapter and the actual JSON comparison check passes.

The first broad run was blocked by Windows sandbox loopback restrictions. The
stopped controlled fixture left its own admission marker in the default workspace
path; this exposed CLI tests using shared runtime state. Those tests now use
per-test admission directories and passed with the unrelated marker still present.
Only the marker belonging to that verified terminated fixture PID was then removed;
no real model runtime was stopped or automatically recovered.

A subsequent approved socket-capable full run passed all gates. The controlled
web run logged an h11 closed-connection error during test traffic while all six
browser cases passed. No failed check or failed assertion was hidden.

## Configuration and scope decisions

The owner selected one command plus a readable browser report in the asynchronous
question on 2026-11-08, confirming the implemented first slice. No app API/database migration or
new YAML configuration is introduced. An ignored root `.env` was created from the
existing local Langfuse configuration without displaying values; no existing `.env`
was overwritten, the legacy file was preserved, and tracing defaults off. Runtime
TXT loading is removed. Other interfaces still use process environment values.

Impeccable's typography/radius findings are advisory exceptions for the standalone
reading report; the incumbent palette and text conventions are preserved. Its
pre-existing stale design sidecar was not regenerated. Historical pre-contract
reports require their matching source environment rather than implicit migration.

## Completion and delivery

Implementation and functional acceptance scenarios are complete and verified;
F-011 is in completed. The selected workflow's staged/committed handoff gates run
at the commit boundary; their receipts and exact revision accompany the handoff.
Owner review of this delivery is separate from the verified functional scenarios.
F-004 model-quality baseline/thresholds/freeze remain open. No real model-quality
run, held-out inference, remote tracing request, push, PR, merge or deployment was
performed. The unrelated pre-existing `outputs/reviewer-workflow.html` is preserved
outside the commit. Completion date: 2026-11-08.
