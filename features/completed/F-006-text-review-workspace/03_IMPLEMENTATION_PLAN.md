# F-006: Text review workspace plan and evidence

Status: completed local functional implementation and verification, 2026-11-07, under SRC-021/SRC-022. Branch codex/f-006-review-desk; unpublished. Model quality, final audio, owner operational feedback, merge and deployment remain separate.

## Initial design workflow and scope (historical)

project-workflow orchestrates. House planning-workflows is the lead for the cross-feature scope/contract/document update. Inspected pstack architect: its multi-model architecture arena and implementation loop exceed this design-only deliverable. Impeccable is the supporting visual workflow: actual Windows context launcher, init/shape/new-work/Operate/craft-floor guidance, concept seed, rendered visual verification and finish review. verification-before-completion supports evidence. No full pstack architect/Feature, full Impeccable shape stop, production stack setup, or model-quality evaluation is claimed.

The detailed owner handoff settles product audience, stack, invariants, and the request for two finished alternatives before choice. Following that explicit instruction, captured PRODUCT.md from supplied facts and adapted the skill's usual pre-build interview/choice into a post-render comparison. No owner visual selection/default has been invented. App screens use code-first. Initial roll lacked network access; one authorized retry returned catalog challengers. Seed reference: seed:15bb05bc61674be4. The visual exploration record is in the [surface brief](../../../docs/TEXT_REVIEW_DESIGN_BRIEF.md). No generated raster artwork or fonts were needed; screenshots are browser captures.

Verified branch codex/text-review-dashboard at 18f8677 before editing. During this task the owner merged PR #2 and requested synchronization. Fast-forwarded to c82f0ed8179e583ce9d25f4acd027a0898bc4536; origin/main is an ancestor and the tree has no file differences from 18f8677. PR #1 was merged at 9abcb84; PR #2 is now merged, not an open dependency. Existing .archify/ preserved. No checkout, commit, push, PR or deployment requested.

## Verifiable slices

- [x] Split frontend/API acceptance into substantial F-006; keep F-004 core/evaluation/audio ownership and map the former UI criteria explicitly.
- [x] Record approved Next.js/Nginx/proposed FastAPI direction, text-before-audio sequence, and proposed API job/version/review/error contracts.
- [x] Produce two distinct interactive static layouts with the same fictional cases, no data/core/API imports, and clear simulation labels.
- [x] Verify rendered desktop/narrow states and focused prototype behavior; record independent review and checks below. Documentation/immutable check outcomes are recorded separately.
- [x] Owner selected A Review desk and authorized implementation under SRC-021 (2026-11-06).
- [x] API/storage slice: strict routes, append-only versions/reviews, idempotent jobs, shared CLI/API admission, crash recovery and bounded safe errors; synthetic contract/worker tests.
- [x] Next.js slice: selected layout, explicit submissions, poll/reconnect, exact evidence, versioned edits and run/review history; configure frontend lint/type/browser gates before source implementation.
- [x] Nginx local integration: relative /api routing, body limits and foreign-origin mutation rejection; prove one origin and private service bindings.
- [x] Production browser acceptance against actual Next.js/Nginx/FastAPI with a controlled Ollama HTTP fixture; live development/model-quality measurement remains separate F-004 work.
- [ ] Return to F-004 final audio stage: provision/verify transcription, integrate independent audio selector/upload and version provenance, then paired-audio/resource handoff checks. No early audio installation.

Fresh callback-text-v2 development baseline and candidate freeze remain F-004 work. F-006 prototypes do not depend on them; they cannot establish model-quality acceptance or unblock held-out use. D-004 remains open. Formal held-out execution is separate and never part of this iterative workspace.

## Production browser acceptance plan

1. With a counted fake inference endpoint, change model/filter/case/run, type/save text, record a review and reload; assert zero submissions until Classify. Submit once, double click, retry the identical key and simulate response loss: exactly one job/run. A second tab receives busy rather than parallel inference.
2. Edit v1 to v2; submit v2 with a selected model; inspect v1 output and exact quotes, then reload. Both immutable transcripts, outputs, model snapshots and their provenance remain available. Selected run must govern highlight text. Test Unicode, long lines, duplicate quote occurrences, multiple evidence quotes and empty/over-limit input.
3. Poll a running job across navigation/reload/disconnect; no resubmission. Inject timeout, malformed output, missing runtime/model, context overflow, storage failure and process interruption. Every failed run lacks a policy outcome and retains earlier successes. No automatic retry, fabricated progress or hidden fallback.
4. Disagree with a model and save a human decision; append a correction. Original model output, earlier review events, policy, candidates, approval and gold hashes stay unchanged. A development load exposes no answers. Held-out IDs/routes/files are inaccessible through the app.
5. At 1440px and 390px, use keyboard alone through filters, case selection, editing, submit, status/recovery, history and provenance. Check focus, contrast, live status and long-content overflow. Intercept browser traffic to show one origin and no inference from unrelated controls.

## Design evidence

See [prototype comparison](../../../prototypes/text-review/index.html), [prototype verification notes](../../../prototypes/text-review/README.md), and screenshots there. Local simulation behavior is separate from production acceptance. Final commands and reviewer disposition are recorded after execution.

## Meaningful deviations and next action

Streamlit and the old audio-before-dashboard sequence are superseded by SRC-020. Frontend/API became its own feature because it has separate state, contracts, and browser acceptance; F-004 remains active for evaluation acceptance and the final audio stage. Old batch numbers remain in historical execution records only. Two rendered alternatives precede visual choice per owner instruction. That design-stage next action was resolved by SRC-021; SRC-022 directs production completion on codex/f-006-review-desk. Hosting remains undecided.

## Historical rendered verification and review, 2026-11-06

Used the existing cached Playwright package and existing Chromium headless shell; no production stack or browser install. node prototypes/text-review/verify.cjs with PLAYWRIGHT_MODULE and CHROMIUM_EXECUTABLE pointing to those local installations passed both directions. [verification.json](../../../prototypes/text-review/verification.json) records checks: explicit submission, versioned editing, retained original text/highlight, separate human review, reload history, loading, timeout, malformed/unavailable, empty/no-filter-results, long content and 390px overflow. Added review-driven assertions cover edited-text highlights, history visibility during busy/unavailable, focus preservation and Casebook DOM order. Screenshots are full-page from top at 1440x1000 and 390x844 viewports; all 18 were independently inspected.

Initial launch looked for an absent default browser build; explicitly selected the installed executable. Intermittent headless capture-protocol failures were rerun; only completed passing capture sets are final evidence. These were capture failures, not model/runtime results. No dependency was downloaded. node --check passed workspace.js and verify.cjs.

Impeccable detector ran once on HTML/CSS/JS, exit 1 with two warning-level marquee matches for the intentional indeterminate loading animation. The fresh independent finish reviewer judged them nonmaterial with reduced-motion disabling animation. First review requested fixes for edited quote highlights, history during processing, misleading model-switch copy, focus/DOM order and empty wording. One correction batch plus full recapture passed reviewer verdict: ship at prototype scope for owner comparison; all listed fixes resolved. [Review record](../../../prototypes/text-review/REVIEW.md) preserves scope and limitations. No full production accessibility or API acceptance is implied.

The prototype has one configured classifier; no unconfigured alternative is invented. All inference, timing and outcomes are simulations. No model digest/hash is fabricated. Browser storage is prototype-only. Production AC02–AC10 remain unchecked, and visual choice remains the owner's next step.

### Final documentation and integrity checks

The shared command .venv/Scripts/python.exe scripts/check_project.py --suite docs passed: quality-baseline configuration, 206 local links, feature lifecycle and CI structure. The initial attempt correctly reported the not-yet-written DESIGN.md link; reran after the documenter completed it. Frozen release check scripts/freeze_gold.py --check verified 40 unchanged cases. Git comparison against c82f0ed returned no changes for accepted policy, candidates, approval or gold, and no changes to src/tests/config/dependency manifests. git diff --check passed. A UTF-8/final-newline/trailing-whitespace scan passed 19 new text artifacts; design sidecar JSON schemaVersion 2 parsed. Independent documenter extracted and validated actual tokens into DESIGN.md and .impeccable/design.json, explicitly preserving both directions as unselected prototype evidence.

A static preview bound only to 127.0.0.1:8765 serves prototypes/text-review; its comparison page returned HTTP 200 and comparison.png was inspected. The restricted loopback preview attempt was denied, and a broader local-access retry initially timed out against the sandboxed server; restarting that static server with local access resolved it. No external hosting occurred. The 18 state/layout captures plus one comparison capture are browser output from the local artifacts.

Full Python tests, package/static suite and staged/committed snapshot preflight were not rerun: this is an uncommitted design/document/static-simulation review, with no application-core/config/dependency changes or publication boundary. Earlier parent snapshot evidence is historical, not newly claimed. Production frontend checks, API contracts/admission/restart, real Nginx routing, full accessibility and actual live model acceptance remain unrun until implementation. branch-finish/preflight guidance was inspected for final scope/hygiene; no clean-snapshot or merge-readiness claim is made. All design work remains local and unstaged on codex/text-review-dashboard at c82f0ed; unrelated .archify/ is preserved. No production implementation, live inference, freeze, held-out run, audio installation, model download, commit, push, PR, merge or deployment was performed by this design task (the fast-forward incorporated the owner's already merged PR #2).

## First production backend batch, SRC-021, 2026-11-07

Owner selected A Review desk and said to update docs, use the workflow and begin. Created and verified codex/f-006-workspace-api from c82f0ed, preserving every design artifact and unrelated .archify/. House planning-workflows remains lead after comparing architect; service-layer-design, error-handling and eng-code-quality support the already specified API boundary. The first verifiable implementation unit is Python workspace/API/admission; Next.js and Nginx follow. No application acceptance or deployment is claimed.

Implemented strict workspace contracts; transactional SQLite case/version/job/run/review storage; shared OS admission and explicit recovery; one background classifier worker; FastAPI routes; three newly authored fictional development inputs; immutable core JSON results and source/model snapshots; safe local Host/Origin/nonce/body boundaries; bounded filters/history; and generated OpenAPI. CLI classify/evaluate now share the default admission directory. No new prompt, scorer or inference provider. FastAPI/Uvicorn and their minimal dependency closure are hash-pinned; AnyIO's Python 3.10 exceptiongroup dependency is explicitly conditional. No telemetry exporter/SDK extra is installed.

Meaningful deviations: embedded SQLite replaces the initial per-file JSON workspace proposal to make multi-record/idempotency changes atomic without a server. Bounded offset pagination replaces cursors for the first local implementation. Parent-version CAS replaces If-Match. Development load has a dedicated explicit route. Interrupted jobs carry an interruption error without a fabricated classifier run. Exact current payloads are documented in the specification and generated OpenAPI. The selected visual design remains A; the existing prototypes stay simulations until the production frontend slice.

Validation before source implementation: scripts/check_quality_baseline.py passed. Initial synthetic route tests found an unsuitable recursive JSON alias for a stored source snapshot; reused the existing SourceIdentity contract. New context-manager types and explicit TypeAdapter annotations satisfy strict typing without runtime-contract changes. SQLite connections now close deterministically. Sandbox Windows asyncio/HTTP fixture access was denied; broader local-socket runs are the valid evidence. Editable install succeeded after using repository-local temporary storage. No model call or held-out read was used.

A first full shared check passed 108 tests plus Ruff/format/Pyright, data/docs/lifecycle checks and offline clean-wheel dependency/import/CLI verification. An additional interrupted-worker regression increases the intended final count; final evidence is recorded after rerun. The focused API tests cover: explicit counted submission, idempotency, edits and old versions, preserved success/failure history, separate append-only reviews, SQL immutability, busy API plus actual CLI classify/evaluate contention, crash/recovery ordering, input/origin/nonce/size errors and no inference from development/filter operations.

Independent read-only review proved a recovery-order issue: clearing a marker before API restart left a durable job running. Startup now reconciles orphan jobs while holding OS ownership, regardless of marker existence; both recovery orders have regression coverage. Review also identified non-ASCII compare_digest input; byte comparison and a safe-error regression fix it. The review agent subsequently hit its tool usage limit before returning a complete final review. These proven corrections are addressed; a completed independent review is not claimed. Primary self-review and configured gates remain required.

Current status: backend unit implemented with focused evidence; F-006 stays active. Next.js A, Nginx one-origin wiring, production browser acceptance, complete accessibility, and separately authorized live model integration are still unchecked. No live inference, model download, freeze, held-out evaluation, audio work, push/PR/merge or deployment is part of this batch.

### Backend checkpoint verification

Final focused API run passed all eight tests after the interrupted-worker and non-ASCII nonce regressions. Ruff and strict Pyright pass. The first full run passed 108 tests before the final worker test; the staged pre-commit snapshot below is the final staged target, now 111 tests after the transport regressions and must finish successfully before any local commit. It also checks generated OpenAPI, immutable data/docs and offline clean-wheel/API import behavior. Core policy/candidate/approval/gold have no changes. No completed independent-review verdict, production browser acceptance or overall F-006 completion is claimed.

The next implementation slice is the selected A Next.js workspace, followed by local Nginx wiring and browser acceptance. Existing static previews do not substitute for it. A live development/model-quality run and final audio remain separate, unperformed work. The owner asked whether the feature was complete; the status answer was no, with backend verification continuing. F-006 remains active.

### Transport-completion correction

Primary self-review found that closing a timed-out HTTP transport does not prove provider quiescence. API and CLI classification now retain recovery admission for ambiguous transport failures; the saved failed job remains visible. Evaluation saves the failed prediction and aborts before another request or answer read. Added a regression proving one request only, retained failed artifacts and no report/answer access. Completed-report failure-denominator fixtures now use known-terminal invalid_output; pure timeout metric tests remain. This is an intentional resource-safety behavior change, not a model-quality result. The final snapshot must include these corrections and updated tests before a local commit.

Final behavior rerun passed 110 tests before the added direct CLI-timeout regression. The final staged snapshot target is 111 tests, including that regression. Generated OpenAPI and 208 local links were verified. Only the final staged snapshot result authorizes a local checkpoint commit; no F-006 completion is implied.

### Observed checkpoint result, 2026-11-07

.venv/Scripts/python.exe scripts/codex_preflight.py --mode pre-commit passed the staged backend snapshot after transport corrections: 111 tests, Ruff/format/Pyright, immutable 40-case checks, 208 local links/OpenAPI/lifecycle checks and offline clean-wheel dependency/API import/CLI checks. Final documentation-only status clarifications were then checked with the docs suite and git diff --check; application source is unchanged from the passing snapshot. No local commit or publication was made. A future commit must run a matching snapshot gate after any further edits. The working batch remains local on codex/f-006-workspace-api; unrelated .archify/ is untouched.

F-006 is not complete. The user-facing Next.js A Review desk, actual Nginx single-origin integration and full browser/accessibility acceptance remain unimplemented/unverified. Backend implementation and synthetic verification do not satisfy those criteria. No live inference, model quality acceptance, held-out action or audio work occurred.

## Completion run, 2026-11-07

The owner explicitly requested continuation to F-006 completion. Verified and switched to codex/f-006-review-desk, carrying the staged backend/design checkpoint intact. House planning-workflows continues after comparing architect: selected A and established contracts remove the need for another architecture arena. TypeScript discipline and Impeccable Operate/craft-floor support the frontend. No new visual workshop or product interview reopens the approved direction.

Execution units: configure web lint/type/build/browser gates and locked dependencies; complete typed OpenAPI responses needed by the client; implement A with explicit version/model submissions, idempotency/reconnect, immutable history/evidence and separate reviews; add loopback Nginx configuration and reproducible startup; drive actual production Next.js, Nginx and FastAPI against a controlled Ollama HTTP fixture; inspect desktop/narrow states and accessibility; finish review/docs/acceptance evidence; run final local/snapshot gates. Live inference/quality, frozen candidate acceptance, held-out evaluation, audio, deployment and remote publication remain excluded. No completion claim until all F-006 functional acceptance criteria have evidence.

### Production implementation and observed verification

Next.js production A uses a generated OpenAPI TypeScript contract plus Ajv boundary validation, explicit save/model/submit actions, global busy status, persisted idempotency keys and GET reconciliation, immutable input/run/history rendering, exact repeated/overlapping evidence, separate review events and provenance. The API adds typed composite responses and read-only global jobs, accepted-submission lookup and per-run review pagination. No prompt/scorer fork. SQLite schema version remains 1. Nginx is loopback-only and actual /api browser traffic stays on one origin. Start with scripts/run_review_desk.py after the explicit setup guide commands.

Two actual-stack Playwright flows pass. They count controlled Ollama HTTP requests and prove explicit execution, no selector/edit/review/reload inference, response-loss recovery without duplication, second-tab/API rejection, old-version evidence after edits, original human disagreement after backend restart, failures without policy labels, timeout admission recovery, interrupted-worker rendering, UTF-8 limits, long Unicode lines, recoverable save/API errors and keyboard focus/review/provenance. Desktop 1440px and narrow 390px axe WCAG 2/2.1 A/AA scans report zero violations. Primary rendered inspection and the independent finish review cover actual captures. Initial test failures were synchronization/locator issues; a genuine missing editor focus and stale terminal notice were corrected. Only successful current captures are evidence.

The focused API suite passes 12 tests, including new reconnect/pagination and safe storage-error tests. The previous full backend snapshot had 111 total tests; the new total is 114, verified in the full behavior suite and required again in the final snapshot. Python Ruff/format/Pyright pass after all new scripts. Production build passes. Generated client/schema consistency, complete behavior/data/docs/clean-wheel and frontend checks remain required in the matching staged snapshot below.

Impeccable detector ran once on changed production web targets: zero findings. Fresh independent visual review initially requested one P2 correction for stale processing copy after terminal jobs. Corrected, rebuilt and recaptured; reviewer verdict pass: ship, original finding resolved, at correction-list scope. See [review](../../../docs/evidence/F-006/REVIEW.md) and [evidence](../../../docs/evidence/F-006/README.md). Backend independent review limitation remains recorded above; primary review and gates do not imply an unavailable independent approval.

| Criterion | Evidence and result |
| --- | --- |
| AC01 | Two historical directions, prototype verification/independent review and owner selection A under SRC-021. |
| AC02 | Browser explicit paste/load/model/Classify flow, request counting, no unrelated-control inference, lost-response reconciliation; API same-key replay tests. |
| AC03 | Browser v1/v2 saved text, old-run restore during processing and after restart; API CAS/stale-parent and immutable storage tests. |
| AC04 | Real classifier/validator over controlled HTTP, exact repeated/overlapping quote display and accepted rule/reason; errors have no outcome. |
| AC05 | Separate disagreement survives restart; API append-only correction, idempotent event and per-run pagination tests; gold integrity checks. |
| AC06 | Empty, loading/history, malformed, unavailable, timeout/recovery, limit and interrupted captures; API/core busy/context/storage boundaries. |
| AC07 | Browser/API restart retains original transcript, run provenance and human review; explicit technical disclosure. |
| AC08 | Actual Nginx production-stack browser requests all use origin 127.0.0.1:18880; config binds services to loopback; API rejects foreign origins, nonce/shape/body/stale violations. |
| AC09 | Desktop/narrow rendered inspection, zero axe violations, long Unicode/line overflow test, keyboard editor/save/review/provenance focus flow and named status/error recovery. |
| AC10 | API/actual CLI contention, second browser/API rejection, same-key replay, crash/recovery ordering and uncertain transport markers. One executor, no queue/provisioning. |

Acceptance is functional within F-006 scope under the owner's continue-to-completion instruction. New model-quality measurements, fresh development baseline/freeze, held-out execution, final audio, hosted CI, merge and deployment are not verified by these results. The branch remains local and unpublished. Final matching snapshot outcome is the completion/commit gate; no checker result is inferred from this plan text.

### Final recovery review and acceptance

A fresh independent backend reviewer reproduced a P2 startup ordering gap: if the API starts during healthy CLI ownership, orphan reconciliation was skipped permanently. JobService now retries deferred reconciliation when OS ownership becomes free, before submission/replay; a global sync API dependency also covers read/poll requests. The regression proves it preserves the live CLI owner and then interrupts the orphan for both a new key and original-key replay. All 12 API tests pass. The reviewer independently executed both isolated regression branches and scored the finding resolved; its separate ASGI setup stalled in Windows socketpair creation and was stopped. No other actionable finding was identified within its traced backend scope.

Observed local gates after that correction: all 114 behavior tests pass; Ruff/format/Pyright pass; OpenAPI/docs checks pass; the full web suite passes locked installation, exact generated types, Biome, strict TypeScript, production build and both browser flows. Immutable data and clean-wheel gates passed in the shared run; the final staged snapshot repeats all suites against the exact index. One prior web attempt failed to overwrite an existing screenshot with a transient Windows file-open error; the subsequent complete run passed. A generated-client formatting drift was resolved by regeneration, with generated code excluded from formatting edits. No product behavior failure is masked by test retries.

All F-006 criteria now have evidence in the matrix above, so the feature moves to completed. The remaining unchecked audio handoff is a separate F-004 feature responsibility. Final publication state: local branch only, no push/PR/merge/deployment. The required staged preflight must pass before the local commit; its command output is the gate, not this narrative. A later commit may record its observed result without changing application code.
