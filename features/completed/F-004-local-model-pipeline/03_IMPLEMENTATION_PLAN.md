# F-004: Local model pipeline implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).
Status: completed for the retained text scope on 2026-11-08 by owner testing and QA acceptance, SRC-026. The current-source callback-text-v2 development baseline is validated. F-011 extends the original evaluator with one command, readable reports, and compatible saved-run comparison, merged through PR #7 at 98a2d5b. F-006 owns the text workspace. Audio is deferred under SRC-024; actual candidate freeze, real held-out measurement, and numeric production-quality targets remain explicit follow-up work. Dated execution sections below preserve historical scope and observations.

## Owner QA closeout, SRC-026, 2026-11-08

The owner stated, "we can close f-004 i did the testing and qa," and requested a documentation cleanup branch and evaluation references in the engineering map. This is owner acceptance of the retained text delivery. It does not assert that a candidate was frozen, that real held-out inference ran, or that a numeric production threshold was selected. Those remaining activities are tracked in the [roadmap](../../../docs/ROADMAP.md#model-quality-and-release-follow-up).

The implementation and tests are already merged. F-011 [PR #7](https://github.com/aidevcode9/voice-callback-review/pull/7) merged at `98a2d5b079fe129cc67fdc68e7b7e40fceef7acf`. Its final implementation revision is `7302c3356143c2d435db1615d4467e37611d8ca9`. The [F-011 plan](../../completed/F-011-evaluation-workflow/03_IMPLEMENTATION_PLAN.md) records the fixes and prior verification. The final local receipts `.test-work/f011-fix-precommit.log` and `.test-work/f011-fix-prepush.log` record all selected checks passing with 167 Python tests and six production-stack browser flows. These are prior verification results, not newly rerun for this documentation change.

### Fresh development evidence

Saved run `4280e453-bf5a-42f8-80c8-b11ae767ce22` started at `2026-11-09T00:26:35.102133Z` (November 8 in the owner's timezone). It used clean revision `7302c3356143c2d435db1615d4467e37611d8ca9`, `callback-text-v2`, `qwen35-4b`, and gold v1.0 development inputs. Its source fingerprint `bb5cd4ce59a5a3326ed6c04009e24f3efeeefc16f7e4c9957dbc3c9b88da4ca8` matches merged main's package and prompt bytes.

On November 8, saved artifacts were revalidated with `load_review(Path("reports/text/4280e453-bf5a-42f8-80c8-b11ae767ce22"), Path("data/gold/v1.0"))` from `voice_callback.evaluation_review`. This checks artifact bindings and callback-score-v1 counts without inference. The run has 20/20 valid outputs and correct labels, callback recall 8/8, precision 8/8, needs-review rate 6/20, and zero unsafe misses or processing failures. The report SHA-256 is `65284d6b270697f5f03095bc1f8f6b826eec893dbd2004b166bf9283d7ff49a7`.

The ignored run directory includes `review-baseline-5d2b3bafcc265941c01fc55bd362590b07f49a95dce241a6b5e3672284316801.html`. Preserve the directory separately when moving machines. This fictional development result does not measure unseen-case performance or production suitability. Original v1 artifacts and dated evidence below remain unchanged.

### Final acceptance mapping

| Criteria | Closeout disposition |
| --- | --- |
| AC01–AC02 | Implemented diagnostics, explicit registry, selected local Qwen classifier, and missing/incompatible-model failures. Batch 1/2 offline and live evidence below; owner QA accepted retained classification scope. |
| AC03–AC05 | Implemented strict output/evidence validation, separate processing failures, immutable transcript-bound provenance. Batch 2 evidence and F-006 controlled browser acceptance; owner QA accepted text delivery. |
| AC06 | Implemented scoring with explicit denominators and failures. Fresh v2 development evidence above plus F-011 readable reports and saved comparison. |
| AC07 | Implemented guarded frozen-system path and input/answer isolation, verified with synthetic tests. SRC-026 closes the text delivery and transfers actual candidate freeze and real held-out measurement to quality follow-up. No real held-out result is asserted. |
| AC08, AC10, transcription part of AC02 | Deferred to the audio roadmap under SRC-024. Not implemented or accepted as audio capability. |
| AC09 | Transferred to completed F-006-AC03/AC05, with controlled browser evidence in its plan. |

### Documentation cleanup workflow

Branch `docs/f-004-closeout-evaluation-map` was created from main `98a2d5b` before edits. Project-workflow selects pstack technical-writing as the lead for this bounded documentation closeout, with unslop and verification-before-completion supporting it. House planning-workflows was considered; no new implementation design or architecture playbook is needed. The cleanup updates living status, transfers, links, and the HTML map, while preserving dated execution history. SRC-027 expands the roadmap for technical-team handoff, including production hardening, deployment, and automated CI/CD. Verification uses the shared docs suite, whitespace/link checks, and rendered desktop/narrow HTML inspection. No new model run, candidate freeze, or real held-out execution is part of this branch.

## Original batch 1 workflow and ownership (historical)

Use project-workflow as the orchestrator and house planning-workflows as the lead. House planning-workflows, pstack Feature, and architect were inspected again for implementation. House planning fits the agreed module design and bounded diagnostics batch. Pstack technical-writing and unslop support the documents; verification-before-completion supports evidence. No full pstack Feature, architect, or delegated implementation run is claimed.

The user requested this GPT-6.1 Sol high-reasoning chat for batch 1. The previous planning chat finished its documentation before implementation began. This chat owns the coupled batch and shared implementation plan; no concurrent writer was used.

## Original batch 1 throughput and shared state (historical)

- Blocking first steps: read AGENTS, PRD, this feature, and the profile; inspect the working tree; keep frozen data unchanged. No classifier choice is needed for batch 1.
- Independent workstreams: later UI and audio experiments can separate only after shared types and contracts exist. No fan-out is needed for batch 1.
- Shared mutable state: one implementation owner writes model configuration, runtime contracts, and this plan. Inference runs get separate directories; gold stays read-only.
- Smallest safe decomposition: one owner for the coupled diagnostics, registry, and CLI slice. It can prove useful behavior without downloading a model.

## Verifiable batches

- [x] Batch 1: package, contracts, runtime health, and model registry. Create pyproject.toml, domain.py, models.py, ollama.py, cli.py, config/models.json, and focused tests. doctor reports the current server and empty-model status; models distinguishes configured from installed and compatible. No classifier default, model downloads, sign-in, inference, audio installation, or dashboard work. Update setup documentation and observed evidence.
- [x] Batch 2: selected text classifier. Owner selected qwen3.5:4b-q4_K_M before explicit provisioning. Implemented the accepted-policy prompt, structured response validation, provenance, exclusive run records, and classify CLI. Offline checks and focused development inference verified outcomes, evidence, identity, and failure behavior. See the execution record below; formal evaluation remains batch 3.
- [x] Batch 3 text implementation and development verification: scoring, immutable artifacts, strict contracts, candidate-freeze command, and guarded held-out path are implemented. The fresh callback-text-v2 development baseline is validated below. Actual candidate freeze and real held-out execution are transferred to the quality follow-up under SRC-026; neither is claimed complete.
- [x] Text workspace handoff: F-006 owns Next.js/API/Nginx, explicit text submissions, versioned editing, result/history, separate human decisions, case filters and browser acceptance.
- Deferred, not completed: former transcription and paired-audio stages, including AC08, AC10 and the transcription part of AC02, are transferred to the roadmap under SRC-024.
- [x] Review the retained acceptance criteria and transfers, record owner testing and QA acceptance under SRC-026, and move F-004 to completed. See the closeout mapping below. Numeric production-quality targets remain D-004.

Each batch ends in a verified state before dependent work starts. A future audio feature needs its own scope and acceptance ownership.

## Commands and evidence

Existing commands below are available now. Planned commands must be implemented in their batch and verified before being reported as passing.

| Acceptance or check | Batch | Exact command or scenario | Expected evidence | Observed result |
| --- | --- | --- | --- | --- |
| Frozen release integrity | Every affected handoff | python scripts/freeze_gold.py --check | Existing 40-case release unchanged. | Batch 1: .venv\Scripts\python.exe scripts/freeze_gold.py --check verified v1.0, 40 cases unchanged on 2026-11-05. |
| Existing behavior | 1 onward | python -m unittest discover -s tests -v | Existing tests and new focused offline tests pass. | Batch 1: .venv\Scripts\python.exe -m unittest discover -s tests -v passed 49 tests on 2026-11-05, including the existing 22 and 27 new behavior tests. |
| F-004-AC01 | 1 | python -m voice_callback.cli doctor | Server version, connection status, and empty or populated model list. | Batch 1: .venv\Scripts\python.exe -m voice_callback.cli doctor exited 0; server 0.40.14, zero installed models, inference_verified false. |
| F-004-AC02 | 1 | python -m voice_callback.cli models --stage classification | Configured choices with distinct availability; only installed compatible choices selectable; no download. | Batch 1: .venv\Scripts\python.exe -m voice_callback.cli models --stage classification exited 0 with no configured classifier or invented default. |
| F-004-AC01 and AC02 | 1 | Stopped server, timeout, malformed HTTP response, incompatible and missing model fixtures | Useful status and appropriate process exit; no model selected implicitly. | Controlled offline behavior verified in test_ollama.py and test_models.py, including exact stage/tag joins, refusal, timeouts, malformed JSON/schema, redirects, HTTP errors, response caps, premature bodies, and no defaults. |
| F-004-AC03 through AC05 | 2 | .venv\Scripts\python.exe -m voice_callback.cli classify --input data/gold/v1.0/inputs/development.jsonl --case-id VC-001 --model qwen35-4b | Valid result or explicit failure with provenance. | Implemented; VC-001 returned callback_required / UR-001 with exact transcript quotes and model/prompt/policy/transcript provenance. See batch 2 record below. |
| F-004-AC06 | 3 | python -m voice_callback.cli evaluate --split development --model MODEL_ID | Complete counts, failures, denominators, and inspectable predictions and scoring report. | Implemented and offline verified; historical v1 evidence preserved. Validated callback-text-v2 run 4280e453-bf5a-42f8-80c8-b11ae767ce22 matched 20/20 labels; see closeout below. |
| F-004-AC07 | 3 | Synthetic freeze/held-out boundary checks; actual run requires explicit opt-in and matching freeze | Input-answer separation, configuration hashes, drift rejection. | Implemented and offline verified in F-004/F-011. No real held-out inference or candidate freeze is claimed; actual measurement is transferred to quality follow-up under SRC-026. |
| F-004-AC08, AC10 and transcription part of AC02 | Future roadmap | No current command or delivery gate | Future feature defines acceptance and verification. | Deferred, not run or accepted. |
| Former F-004-AC09 -> F-006-AC03/05 | F-006 | Explicit submission, versioned edits and separate review | No automatic inference; earlier results remain inspectable. | Controlled browser evidence is recorded in the completed F-006 plan. |
| Documentation | Each batch | git diff --check and local Markdown link inspection | No whitespace errors or broken changed-document links. | Batch 1: git diff --check passed. 146 local Markdown targets in 38 working documents passed; whitespace in all 14 untracked files passed. Bundled template assets excluded; see execution record. |

Use the project virtual environment. Batch 1 must document its editable installation command and supported Python version so package entrypoints are reproducible. Optional audio and dashboard dependencies remain separate from the first batch.

## Blockers and decisions

SRC-018 resolves the classifier choice and authorizes provisioning and development inference. The selected Qwen model is installed and exercised. SRC-026 accepts the retained text feature after owner testing and QA. D-004 numeric production-quality targets remain open; report measured development counts without inventing a pass threshold.

SRC-020 rejects Streamlit. F-006 implements the Next.js/API workspace. SRC-024 moves audio to the roadmap; earlier audio limits and model suggestions are unaccepted historical proposals.

## Batch 1 pause and handoff (historical)

Current checkpoint: batch 1 implemented and verified in the project .venv. The feature is active and only batch 1 is checked. Frozen policy, candidates, approval, and gold remain unchanged. Existing documentation edits are preserved.
Next action: the owner chooses the callback classifier and exact local tag under D-003 before batch 2 can explicitly provision weights and run inference. No classifier is selected by this handoff. Confirm the Ollama executable path for that setup step; it is absent from this shell's PATH although the server is reachable.
Later batches remain unchecked. No audio/UI dependencies, model inference, model-quality results, cloud access, credentials, commit, push, or publication are part of this handoff.

## Completion and delivery

SRC-026 accepts F-004's retained text delivery after owner testing and QA. The feature is completed; the implementation is merged, while this documentation closeout is on a local review branch. The owner's acceptance covers the prototype text scope. Numeric production-quality targets, real held-out measurement, and hosted deployment remain separate. F-006 owns text workspace acceptance, F-011 owns the evaluation experience, and audio is deferred under SRC-024.

## Batch 1 execution record

On 2026-11-05, implementation re-read project instructions, all F-004 documents, the lifecycle, and the workflow profile. Inspected house planning-workflows, workflow-skill-manager, pstack Feature and architect, and supporting technical-writing/unslop. House planning-workflows remains the lead: the supplied module design and coupled diagnostics slice need one owner, not competing prototypes or delegated implementation. No full pstack Feature or architect playbook is claimed. Review and verification use code-review-workflow and verification-before-completion; branch-finish governs the local handoff without publication.

Git status was reviewed with broader file access because the restricted shell returned a misleading work-tree error. Preserved nine modified documentation files, untracked docs/LOCAL_MODEL_OPTIONS.md, and the three untracked F-004 documents. Verified exact resolved source and destination paths before moving features/backlog/F-004-local-model-pipeline to features/active/F-004-local-model-pipeline, then repaired incoming links.

Validation before coding: standard-library controlled HTTP tests for connection refusal, timeouts, malformed JSON/schema, HTTP errors, redirects, bounded responses, and explicit registry compatibility; CLI behavior checks; full unittest discovery; gold integrity; live doctor and models; local Markdown links; git diff --check. No model provisioning, inference, audio/UI dependency installation, or cloud credentials.

### Actual batch 1 commands and observations

All repository commands ran with working directory C:\Users\dev-user\projects\voice-callback-review. Broader file access was used because the chat's registered workspace is skill-building; no implementation was written there and no repository copy was created.

- python -m venv .venv created the project environment with Python 3.13.1.
- .venv\Scripts\python.exe -m pip install --disable-pip-version-check --no-deps -e . succeeded using pyproject.toml's setuptools 80.9.0 backend. Pip 24.3.1 and voice-callback-review 0.1.0 are the only installed distributions.
- .venv\Scripts\python.exe -m pip check reported no broken requirements.
- .venv\Scripts\python.exe -m unittest discover -s tests -p test_ollama.py -v and the equivalent -p test_models.py focused checks passed. Full discovery then verified all 49 current tests.
- .venv\Scripts\python.exe scripts/freeze_gold.py --check verified 40 cases. Candidate validation and render --check also passed with the original 40-case snapshot.
- .venv\Scripts\python.exe -m voice_callback.cli doctor, models --stage classification, and models --stage transcription each exited 0 against http://127.0.0.1:11434. Ollama 0.40.14 reported an empty inventory. No configured classifier exists; turbo and small remain runtime_not_verified and not selectable. inference_verified is false.
- .venv\Scripts\voice-callback.exe --help verified console registration. The executable was also exercised through the setup guide's doctor command at handoff.
- git diff --check verified tracked-edit whitespace. Local Markdown target checks and untracked-file whitespace checks supplement Git because new package/tests/config/setup/feature documents are still untracked.

The implementation read official Ollama llms.txt, tags, get-version, errors, and show-model-details documentation before final API verification. The version page's browser extraction was incomplete, so its official Markdown contract was fetched directly with a bounded request. Diagnostic requests use only GET /api/version and GET /api/tags. No inference or pull endpoint was called.

The first test run failed because HTTP/1.0 response completion closes its socket before the adapter's next timeout update. A traced OSError 10038 identified that first wrong operation; the loop now stops when the response is closed. Controlled tests also cover total deadlines under continuous slow output and premature body closure. Connection refusal uses a controlled exception fixture because Windows can surface a closed loopback port as a timeout at short deadlines.

Implementation choices: Python 3.10+, no runtime dependencies, pinned editable-build backend, exact configured tag matching with observed digests, null versus empty inventory, immutable copied model settings, and separate RunSuccess/RunFailure types. Optional audio/UI dependency declarations are deferred to their owning batches rather than guessing versions now. No full pstack Feature, architecture prototypes, delegation, or inference-quality measurement was executed.

F-004-AC01 diagnostics are verified. F-004-AC02's registry/availability portion is verified; UI selectors and actual model execution remain later work. Other acceptance criteria have foundational contracts only and are not accepted by batch 1.

### Final handoff review

Final source verification passed 49 tests after deterministic response cleanup, gold integrity, console-entrypoint doctor, and pip check. Live doctor/models retained the empty-inventory observations above. git diff --exit-code -- docs/CALLBACK_POLICY.md data/candidates/v0.1 data/reviews/v1.0.json data/gold/v1.0 returned 0. git diff --check passed.

A Python local-target scan verified 146 references in 38 working Markdown documents, excluding .git, .venv, .test-work, and bundled assets. An initial broader scan also encountered three template-relative links under project-intake/assets/repository that require template instantiation; those unrelated assets were not changed. All 14 untracked files passed final-newline and trailing-whitespace checks. The count includes the pre-existing local model options and feature documents.

Changed implementation files are pyproject.toml, config/models.json, src/voice_callback/{__init__,domain,models,ollama,cli}.py, tests/test_models.py, tests/test_ollama.py, and .gitignore. Added docs/LOCAL_SETUP.md; updated README, documentation map, architecture, workflow selection/profile, and the three active F-004 documents. Repaired F-004 links in existing PRD/intake/model-options documents while retaining prior content. No files are staged, committed, pushed, or published.

## Local commit and review, 2026-11-06

The owner requested a local commit followed by code review. Re-read project-workflow, branch-finish, code-review-workflow, verification-before-completion, and the pstack blast-radius candidate. House code-review-workflow leads the review because this is a bounded new package with coupled HTTP/registry/CLI contracts. Blast-radius was inspected but its full playbook was not selected. No delegated review is claimed.

Pre-commit verification reran all 49 tests, frozen gold integrity for 40 cases, pip check, git diff --check, and an immutable-path Git comparison. All passed. Commit scope includes the batch-1 package, tests, model registry, setup documentation, active F-004 records, and the intentional earlier local-model planning/intake documentation. The earlier handoff's uncommitted state above is a historical snapshot. No push or publication is requested. Review findings are reported against the resulting local commit.

## Quality baseline prerequisite

The owner requested [F-005 engineering gates](../../completed/F-005-development-quality-baseline/01_REQUIREMENTS.md) before batch 2. Ruff/Pyright, the shared local/CI checker, snapshot preflight, and template requirements are owned there. This does not select a classifier or check off any later F-004 batch.

## Batch 2 branch and new-chat handoff, 2026-11-06

The owner requested feature branches for every new feature/batch and a GPT-6.1 Sol high chat for classifier selection. Created feature/f-004-text-classifier before further feature edits or pushes. The branch includes local completion record c5cfdcd for F-005 plus the new branch-policy instructions. No reset, history rewrite, model selection, download, inference, or push was performed during this handoff. The parent chat finishes writing before the new chat begins; the local checkout is shared, so avoid concurrent writes.

The next owner reads AGENTS, README, documentation map, PRD, profile, project-workflow, all F-004 documents, and docs/LOCAL_MODEL_OPTIONS.md. Recheck Ollama/version/inventory rather than assuming the earlier empty state. Research current official model information, compare a few local classifiers that fit the RTX 4070 Laptop GPU with 8 GiB VRAM and roughly 32 GiB system RAM, and recommend an exact Ollama tag. Ask the owner which model to provision; no implicit default, download, or live inference is authorized until that selection is made. The deferred transcription candidates remain unchanged.

Use the established shared quality/snapshot gates and feature-branch/PR workflow. Frozen policy, candidate source, approval, and gold remain immutable. Held-out answers never enter prompts or model-selection tuning. No cloud inference, API keys, audio/UI dependencies, billing changes, or unrequested main pushes.

## Batch 2 execution record, 2026-11-06

Verified feature/f-004-text-classifier before editing. Initial HEAD a8e342a includes c5cfdcd; both unpublished commits were preserved. Used this existing checkout without another repository or worktree. No concurrent writer or delegated implementation was used.

### Workflow and owner decision

Re-read AGENTS, README, documentation map, PRD, build/lifecycle guidance, workflow profile, project-workflow, all F-004 files, model options, and quality checks. Reassessed installed house planning-workflows, pstack Feature, and architect, with workflow-skill-manager discovery. House planning remains the lead for the existing classifier design. Technical-writing/unslop, code-quality, error-handling, self-review, verification-before-completion, branch-finish, and configured preflight support it. Systematic-debugging was used for the observed context-error wording. No full pstack Feature or architect playbook is claimed.

- Blocking first steps: verify branch, accepted policy/data invariants, engineering baseline, current runtime, and explicit owner model choice.
- Independent workstreams: no fan-out for this coupled classifier/HTTP/CLI slice; research and offline preparation did not require a model download.
- Shared mutable state: one owner writes registry, classifier, and plan. Each run has an exclusive UUID file. Frozen data remains read-only.
- Smallest safe decomposition: selection and authorization first, then transport/classifier and focused checks, then live development checks and snapshot validation.

Compared current official Ollama tags and publisher cards for Qwen3.5 4B, Qwen3 Instruct 2507 4B, and Gemma 4 E2B. [Local model options](../../../docs/LOCAL_MODEL_OPTIONS.md) records exact tags, package/context differences, hardware-fit judgments, structured-output limitations, and the later Nemotron question. No comparative callback-quality measurements were invented. The owner explicitly chose qwen3.5:4b-q4_K_M in the question authorizing download and development-only inference (SRC-018). Nemotron 3.5 Super is locally supported but too large for this laptop's memory; it was not downloaded.

### Provisioning and implementation

The restricted shell could not reach loopback. The same read-only doctor command with broader local socket access found Ollama 0.40.15 and zero installed models. nvidia-smi reported RTX 4070 Laptop GPU, 8188 MiB total, 7596 MiB free, driver 566.07 before inference. These free-memory observations are not peak runtime measurements.

Explicit POST /api/pull for qwen3.5:4b-q4_K_M with stream false returned success. /api/tags then reported 3,324,173,934 bytes and digest d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04. /api/show established local GGUF/Q4_K_M, qwen35, completion, false/true thinking controls, and model context maximum 262144. No other weights or optional dependencies were provisioned. The executable remains absent from the shell's PATH, so the documented explicit server API setup was used.

Implemented classify.py, storage.py, classify CLI, selected registry entry, and bounded POST support in the existing HTTP adapter. Inference requires an explicit model ID, pinned policy bytes, input-only JSONL or exact UTF-8 text, model metadata, stable observed digest, and completed schema-constrained output. Validation rejects unsupported rules/outcome combinations and nonverbatim evidence. Processing failures never receive a policy outcome. Every classification record retains versions, hashes, model identity/settings, runtime, case/transcript identity, start, and elapsed time.

Design deviations: individual classification storage was pulled forward so successful and failed development runs retain provenance. Evaluation reports and case/reviewer storage remain deferred. Input is capped at 12000 UTF-8 bytes and 1 MiB per file. The initial request uses context 8192, output cap 768, temperature 0, seed 42, think false, keep_alive 0, truncate false, and shift false. The inspected Ollama 0.40.15 contract supports explicit no-truncation/no-shift behavior; older runtimes are refused. These are development choices without quality acceptance.

### Observed verification

The quality baseline configuration passed before source implementation. The first full shared scripts/check_project.py run passed Ruff, formatting, strict application Pyright, all 72 tests, frozen-data/candidate checks, documentation/workflow checks, and a clean-wheel install/import/CLI smoke test. The 17 new tests cover multiple synthetic subcases for schema/rules/evidence, no label on failure, missing/remote/incompatible models, timeout/size limits, request controls, provenance, input-answer separation, CLI exits, and exclusive storage. Loopback tests ran with socket access; the earlier restricted diagnostic was not counted as a pass.

Live commands used only development inputs and synthetic development text, without opening expected answers for inference or tuning:

| Input | Observed result | Local run ID |
| --- | --- | --- |
| VC-001 | callback_required, UR-001; exact unresolved-issue and representative quotes | 2a4b345a-52a1-44a9-9c9c-c610ca057098 |
| VC-021 | no_callback, NC-003; final resolution preserved | d5c77d08-7b00-4226-896b-1f0ab4f80f12 |
| VC-025 | needs_review, NR-001; incomplete conversation | cf32a02f-b065-453a-8279-f6a55c099333 |
| VC-033 | callback_required, CB-002; request survives resolution | 03c2d96a-ef59-41db-b57f-872c27b9ab2a |
| DEV-CONTEXT-LIMIT | processing_error / invalid_input, no output; actual token overflow rejected | 1617b0e2-bf03-49e4-958c-630355faea73 |
| DEV-INSTRUCTION-DATA | callback_required, UR-001; instruction-like transcript data did not override policy | c67f204b-b530-415c-b618-4b16e84a2be8 |

Records are retained under ignored runtime/classifications. The context check used an explicit 2048-token temporary configuration and a seeded 11000-character synthetic payload. Ollama returned HTTP 400: request of 9361 tokens exceeds available context size 2048. The first adapter mapping reported generic http_error, still without a policy label. Inspection identified the missing context-size wording; a focused regression and rerun verified invalid_input. The synthetic instruction case is one observation, not a general prompt-injection resistance claim.

F-004-AC03 through AC05 have batch 2 functional evidence. F-004-AC02's CLI selection/availability path is implemented; UI selectors remain later. This is neither formal scoring nor overall product acceptance. No held-out inference, evaluation report, audio, dashboard, cloud, sign-in, key, billing change, push, merge, or deployment occurred.

### Current checkpoint

Final working-tree scripts/check_project.py passed all suites, including 73 tests after the context-error and failure-provenance corrections, 159 local links, frozen 40-case integrity, and the clean-wheel smoke test. git diff --check and the immutable policy/candidate/approval/gold comparison passed. Self-review found no remaining actionable issue after retaining prompt/request hashes on runtime failures and respecting shorter connection deadlines. Matching staged snapshot preflight is required before the local commit; no publication is authorized. Keep F-004 active. The next scoped work is batch 3 development evaluation and configuration freeze; its acceptance/quality decision is separate. Batches 3 through 6 remain unchecked.

Final read-only models --stage classification recheck reported the same selected tag/digest and selectable local configuration. GET /api/ps reported an empty loaded-model list after the live checks. This confirms that observation only; peak VRAM and sequential audio/GPU handoff remain unmeasured.

## PR #1 Unicode JSONL review correction, 2026-11-06

The owner authorized publication after batch 2's local commit; PR #1 is open from feature/f-004-text-classifier. This follow-up addresses its P2 reader finding on that existing branch. No new feature or later batch is started.

House systematic-debugging leads after inspecting the pstack Bug fix candidate. The cause is confined to JSONL record parsing, with a cheap focused regression; TDD supplies failing-before/passing-after evidence. No full pstack playbook or delegated implementation ran.

Confirmed that splitlines treats literal U+0085, U+2028, and U+2029 inside valid JSON strings as record boundaries. The new test failed before the fix with 12 ValueErrors across those characters, LF/CRLF record delimiters, and presence/absence of a final newline. The reader now removes one optional final LF and splits only on LF. Transcript characters and exact UTF-8 hashes remain intact. The regression then passed all 12 subcases.

The full shared scripts/check_project.py passed all suites with 74 tests, strict application typing, frozen 40-case integrity, documentation/workflow checks, and clean-wheel smoke tests. git diff --check and the immutable policy/candidate/approval/gold comparison passed. Self-review checked final-newline handling and retained blank-record rejection. Staged and committed snapshot gates remain required before commit/push. No live inference was needed for this parsing-only correction; no held-out data, weights, dependencies, or policy changed.

## Batch 3 execution plan, 2026-11-06

Branch verified: feature/f-004-text-evaluation, based on merged main 9abcb84. The owner requested the next batch through project-workflow. House planning-workflows leads after reassessing pstack Feature, architect, and Eval. The existing classifier and fixed three-outcome rubric need a reproducible single-model runner and deterministic scorer. Multi-model candidates and blinded judging are outside this baseline; no full pstack playbook or delegated implementation is claimed. Explain-the-number supports interpreting counts. Code-quality, error-handling, focused behavior tests, self-review, verification, and snapshot gates support implementation.

Scope: implement development evaluation, immutable input/configuration/prediction/report artifacts, offline rescoring, and an explicit candidate configuration freeze. Implement a guarded held-out path requiring the frozen configuration and an explicit opt-in, but do not run real held-out inference. Audio and dashboard stay unchecked. No new model, dependency, credential, cloud, or publication action is required.

Design: keep the classifier's input-only boundary. Reuse one strict LF JSONL decoder for transcripts, predictions, and answer records so Unicode separators remain data. A frozen dataset reader validates manifest hashes and exact split coverage. The runner receives only transcripts and model configuration; it persists every success/failure and closes predictions before the scorer reads answers. A separate pure scorer joins exact case IDs, counts a three-by-three matrix for valid outputs, and records processing failures by expected label outside that matrix. Missing, duplicate, or foreign predictions are rejected rather than discarded.

Reports expose numerator, denominator, and nullable value for strict callback recall, callback precision, needs-review rate, and valid-output coverage. Strict recall includes callback cases ending in failure or needs_review. Unsafe misses and per-case disagreements remain inspectable. Zero denominators are undefined, not zero or perfect. Run/configuration hashes bind inputs, predictions, model digest and metadata, prompt/policy, runtime settings, and source identity. Configuration drift prevents a completed uniform-system report. Exclusive files and completion markers preserve interrupted work; offline rescoring verifies saved hashes and does not overwrite a differing report.

Files: src/voice_callback/evaluate.py owns orchestration and CLI-facing operations; scoring.py owns reference/prediction values and pure metrics; datasets.py owns frozen split validation; shared JSON helpers and existing classify/storage code supply boundary parsing and exclusive writes. Extend cli.py with evaluate, score, and freeze-evaluation. Existing classify/doctor/models behavior remains tested. Update EVALUATION, setup, architecture, workflow selection/profile, and this feature's specification/evidence.

Verification checkpoints: synthetic scorer examples with all outcomes/failures and zero denominators; exact ID/hash/Unicode preservation; proof that answers are not opened until predictions are closed; interrupted and drifted runs; repeatable offline scoring; held-out rejection without a compatible freeze and explicit opt-in. Then run the shared baseline and snapshot gates. A live development baseline must identify a clean committed implementation and process all 20 inputs without answer leakage. Inspect development mistakes without changing frozen labels or inventing an acceptance threshold. Freeze the baseline configuration for a later separately authorized held-out action.

Decision before measurement: functional failures or unsafe misses require investigation before any quality acceptance. This run does not establish a numeric pass threshold. One trial, one selected model, 20 fictional development cases, and related scenario families limit the interpretation. No repeatability spread, alternative-model comparison, population estimate, or performance result will be inferred. D-004 remains the owner's decision.

Shared-state checkpoint: one owner for the coupled CLI, configuration, and artifact pipeline; pure metric tests can run independently after contracts exist. Frozen policy/candidates/approval/gold are immutable. Every evaluation gets its own exclusive directory. Next step is implementation and offline verification, followed by development-only live evidence.

### Batch 3 offline checkpoint

Implemented the isolated runner, pure scorer, shared strict JSON/LF decoder, frozen dataset reader, configuration identity, offline rescore, candidate freeze, and guarded held-out path. The initial full shared baseline passed 91 tests. One independent read-only review found no actionable issue and independently passed the original 17 synthetic evaluation tests; it did not edit files, read held-out data, or run real inference.

A subsequent implementation self-review reproduced malformed prediction status causing TypeError instead of a validation failure, and generic JSON decoding accepting floating overflow or exposing excessive-nesting behavior. Focused tests made those failures executable. The boundaries now require a string status, reject non-finite parsed floats, and translate excessive nesting into ValueError. These changes remain inside the new artifact/JSON boundaries. Regression and full checks must pass before the clean implementation commit. The live development baseline and final freeze remain pending that commit; no quality result is claimed yet.

The final offline shared baseline passed all suites with 93 tests after the artifact-boundary fixes. Strict typing, lint/format, frozen-data checks, 160 local links/workflow validation, and clean-wheel smoke tests passed. Live doctor rechecked Ollama 0.40.15 and the unchanged selected Qwen digest. The implementation checkpoint will be committed after staged preflight, then the real development baseline will identify that clean revision. No held-out inference or publication is authorized by this checkpoint.

### Preserved development baseline and contract migration

The owner completed development evaluation 7f31782d-c234-4937-85fe-252add830d39 on clean commit 1f9435744cec5cc7952e6bb7a223e66ecdd11a04. Offline rescore reproduced the saved report: 20/20 valid and correct outputs, callback recall 8/8, precision 8/8, review rate 6/20, no processing failures or unsafe misses. The report SHA-256 is ad38e2f72a9ab4d64ccc4700b02c78d8ab901b30ba77b6d597e6818573c7ab01. This is one trial on fictional development cases, not held-out acceptance or a repeatability claim. Preserve all original artifacts under reports/text/7f31782d-c234-4937-85fe-252add830d39.

The owner approved migrating external contracts to Pydantic before candidate freeze, held-out inference, audio, or dashboard work. The stdlib-only bootstrap is superseded for runtime validation. Pydantic enforces data contracts; it does not make inference deterministic or establish semantic correctness.

Workflow reassessed: house planning-workflows remains the lead after inspecting pstack Feature and architect. A coupled boundary migration has established behavior to preserve; competing implementation agents are unnecessary. Code-quality and focused boundary tests support implementation; independent review and verification support completion. No full pstack playbook is claimed. Continue on verified feature/f-004-text-evaluation; preserve its unpublished evaluation commit.

- [x] Preserve and record the pre-migration development baseline before editing source.
- [x] Define strict Pydantic models for registry/settings, transcript input, classifier output, saved runs/predictions, and evaluation configuration/artifacts. Forbid extra fields and coercion; retain duplicate-key, finite-number, size, and LF-only parsing guards.
- [x] Generate the Ollama response schema from the same classifier response model used for validation. Retain policy-rule consistency and exact transcript-quote validation. Keep internal immutable domain values and pure scoring where useful.
- [x] Pin Python 3.10-compatible runtime dependencies and hashes; update environment setup, CI, version checks, and clean-wheel dependency installation.
- [x] Add migration regressions for strict types, success/failure variants, Unicode, schema generation, and artifact integrity. Run the full shared baseline and applicable snapshot gate; review the resulting diff.
- [ ] Commit the verified implementation locally, then have the owner run a fresh 20-case development baseline. A generated schema changes the prompt fingerprint: use callback-text-v2 and preserve v1 artifacts rather than rewriting them.
- [ ] Compare development results and inspect differences before explicit candidate freeze. Held-out inference remains separately authorized; quality targets remain open under D-004.

Files: add contracts.py and requirements-runtime.txt; migrate classify.py, models.py, storage.py, evaluate.py, and evaluation_config.py boundary parsing/serialization. Update pyproject.toml, dependency checks/package smoke tests, CI/setup instructions, architecture, and evaluation guidance. Frozen policy, candidates, approval, and gold remain unchanged. Offline rescore of an old baseline requires its original source revision; migration must not overwrite or relabel that evidence.

Shared-state checkpoint: one implementation owner updates the coupled contracts and callers. Each evaluation keeps its exclusive directory; the existing baseline is read-only. Next step: implement strict contracts and dependency installation, verify them offline, then record remaining live verification explicitly.

### Contract migration implementation evidence

Implemented strict registry/settings, transcript input, CallbackOutput, discriminated saved run/prediction records, and evaluation lifecycle/configuration/report/freeze models. The response schema now comes from CallbackOutput and the prompt is callback-text-v2. Existing domain dataclasses and the pure scorer remain unchanged. The original baseline report still hashes to ad38e2f72a9ab4d64ccc4700b02c78d8ab901b30ba77b6d597e6818573c7ab01. Frozen policy/candidate/approval/gold have no changes.

Pinned Pydantic 2.14.3, core 2.50.4, and the resolved Python 3.10-compatible dependency closure using official PyPI wheel hashes. Setup and CI install the runtime lock explicitly. Clean-wheel smoke tests install those dependencies offline from a prepared, hash-verified wheel cache. Staged preflight shares the cache but verifies the selected tree's lock.

The shared scripts/check_project.py passed all suites with 101 tests, strict typing, lint/format, frozen 40-case integrity, 161 local documentation links/workflow checks, and clean-wheel dependency/import/CLI checks. Eight migration tests cover coercion/extra-field rejection, generated schema use, success/failure separation, Unicode preservation, completion-file rejection, Python whitespace behavior, and safe validation errors. Independent read-only review reproduced a Rust-regex/Python whitespace mismatch for U+001C through U+001F; preserving validators and regressions resolved it, and the reviewer independently passed all eight migration tests with no remaining blocker. Error wrappers also prevent Pydantic discriminator errors from echoing untrusted values.

Read-only doctor rechecked Ollama 0.40.15 and the unchanged selected Qwen digest; it did not run inference. The final staged snapshot gate is required before the local migration commit. Hosted CI and the fresh real development baseline remain unverified. Next: from the clean migration commit, the owner runs .venv\Scripts\python.exe -m voice_callback.cli evaluate --split development --model qwen35-4b. Preserve its new directory, inspect results and offline rescore, then consider candidate freeze. Do not freeze the original v1-prompt baseline as the migrated system. No held-out inference, audio/UI work, push, PR, merge, or deployment is part of this checkpoint.

## SRC-020 scope and sequence update, 2026-11-06

Historical SRC-020 handoff: F-006 owned former AC09 through F-006-AC03/AC05 and UI selection through F-006-AC02/AC08. SRC-024 later deferred F-004's transcription and paired-audio criteria; the current verifiable batches above govern the remaining work.

PR #1 is merged at 9abcb84 and PR #2 is merged into main at c82f0ed. The dedicated UI branch fast-forwarded from 18f8677 to c82f0ed with no code-tree differences. The contract implementation is committed and merged; the remaining checkbox combining commit and live baseline is incomplete solely because callback-text-v2 live baseline/freeze remain pending. The original 20/20 callback-text-v1 development baseline remains historical, not acceptance. No live inference, held-out run, candidate freeze, audio provisioning or quality acceptance occurred in this design task.

### Text workspace handoff completed, 2026-11-07

F-006 completes selected A Next.js, FastAPI/SQLite and Nginx with controlled production-stack browser/API evidence, separate human decisions, immutable version/run provenance, keyboard/accessibility checks and shared gates. Its completed plan maps the former UI criteria. No new live model-quality baseline, candidate freeze, held-out action or audio provisioning occurred. F-004 remains active for text-v2 quality work; SRC-024 defers audio. Earlier dated pending-dashboard statements remain historical.

## Documentation closeout verification, 2026-11-08

The shared docs suite passed quality-baseline configuration, generated OpenAPI consistency, local Markdown targets, feature lifecycle, and CI structure checks. The HTML map was exercised with Playwright at 1440px and 390px in light and dark schemes: no document overflow or JavaScript errors, six evaluation steps, five configured CI jobs, and valid internal anchors. Desktop and narrow screenshots were inspected; the wide delivery diagram scrolls locally on narrow screens. Browser checks blocked the optional remote font stylesheet and verified system-font fallback. Local captures and check receipts remain ignored under `.test-work/docs-map-*`. Full Python/model/application-browser suites were not rerun for this documentation-only change; earlier engineering receipts are recorded separately above.
