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
- Branch: `feature/f-011-evaluation-workflow`, renamed at the owner's request on
  2026-11-08 from `codex/f-011-evaluation-workflow`. It was created at 884168c,
  preserving all unpublished commits and working-tree edits. Implementation is
  committed locally as 5f4ac9a; no source change accompanies the branch rename.
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
| Feature branch | `git branch --show-current` | `feature/f-011-evaluation-workflow`, preserving starting history and implementation commit 5f4ac9a. |
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

## Local branch rename and code review

The owner requested branch rename, local commit and code review on 2026-11-08.
Project-workflow selects code-review-workflow as lead after comparing the pstack
blast-radius candidate; focused executable reproductions support the review.
Branch-finish guides the local-only handoff. The rename record is a documentation
commit, checked with the docs suite and whitespace checks; source remains the
previously verified implementation at 5f4ac9a. Its staged and committed preflight
receipts both passed all suites, including 165 Python and six browser tests.
Independent read-only reviewers cover runner lifecycle and report/baseline
integrity; final findings and limits accompany the review handoff. The unrelated
reviewer HTML and local credentials remain outside commits.

## Code review results, 2026-11-08

Reviewed implementation 5f4ac9a against baseline 884168c. The branch rename and
review-record commits change documentation only. Two P2 defects were reproduced;
their corrections remain open and this review does not approve merging the feature.
Earlier passing acceptance checks remain historical evidence, not proof that these
newly covered scenarios work.

1. **Artifact commands use different source bytes from the canonical run.**
   `evaluation_workflow.py` executes the worker in a committed checkout, but CLI
   `score`/`freeze-evaluation` execute from the caller's package. The project's LF
   attributes allow Git-clean Windows working files with CRLF bytes. A disposable
   synthetic repository reproduced `evaluate` exit 0 followed by `score` and
   `freeze-evaluation` exit 2 because their source fingerprints differed; Git status
   stayed clean and no further model calls occurred. Route artifact operations
   through the recorded source checkout while preserving strict fingerprint checks.
   Local proof: `.test-work/review-f011-runner/repro_line_endings.py`.
2. **Output format changes the offline review exit status.** The same valid
   completed synthetic run containing a processing failure returns 0 from plain
   `evaluations --run-dir`, but 1 with only `--json` added. The JSON branch applies
   `_print_evaluation`'s failure policy and the plain branch returns 0 unconditionally.
   Both formats need the same exit policy. Local proof:
   `.test-work/review-f011-reports/repro_exit.py`.

Fresh focused verification ran
`.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_evaluation*.py' -v`:
37 tests passed. The controlled HTTP integration needed the socket-capable execution
context. The JSON exit-status reproduction was also rerun independently by the
review owner. No additional actionable defect was established in this pass.
No source fixes, live model/held-out runs, real credential reads or remote updates
were performed. The full application/browser suite was not repeated for the
documentation-only rename; the earlier full staged/committed receipts still apply
to the unchanged implementation source.

## Fixing review findings and preparing the PR

The owner authorized fixing both P2 issues, committing, pushing and creating a PR
for review on 2026-11-08. The existing dedicated feature branch is retained.
Project-workflow selects systematic-debugging as lead after comparing the narrow
TDD candidate; regression-first techniques apply because both failures have
existing executable fixture paths. Code-review-workflow, branch-finish and the
configured staged/committed snapshot gates guide handoff. No unrelated change or
real held-out run is authorized by this verification work.

- [x] Reproduce both issues as permanent failing tests before source changes.
- [x] Share committed source context for execution, rescore and freezing without
  normalizing or weakening fingerprints; include the explicitly guarded synthetic
  held-out continuation so freezing does not leave that same mismatch downstream.
- [x] Give successful saved-run inspection status 0 in both output formats;
  execution/scoring failure exits and visible failure counts remain unchanged.
- [x] Run focused green tests; confirm changed source still rejects old artifacts
  and missing held-out opt-in sends no provider request.
- [x] Independent read-only review of the corrections found no actionable issue.

Delivery uses the configured pre-commit and pre-push snapshot gates before
publication. The local receipts are `.test-work/f011-fix-precommit.log` and
`.test-work/f011-fix-prepush.log`; actual gate outcomes and commit identity accompany
the pull request and final handoff. The requested PR is for owner review, not merge.
The two earlier findings are corrected in source and covered by the regression
scenarios below; their original reproductions remain historical review evidence.

Failing-before evidence: the new saved-review test returned 1 instead of 0 with
--json; the CRLF integration test returned 2 from score after a successful canonical
run, with the original source-identity error. Local logs:
`.test-work/f011-red-review.log` and `.test-work/f011-red-source.log`.
Passing-after focused runs: 15 reporting tests, eight workflow tests and two actual
subprocess integration tests passed. The CRLF fixture verifies rescore/freeze make
zero HTTP calls, report bytes are unchanged, missing held-out opt-in is rejected,
explicit synthetic held-out execution succeeds under the freeze, and a subsequently
committed source change still makes score/freeze fail with identity errors.
Verification is synthetic engineering evidence, not model quality.
