# F-004: Local model pipeline implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).
Status: active. Batches 1 and 2 are implemented and verified with offline and live development evidence. The staged snapshot gate is the final commit prerequisite. Batches 3 through 6 remain planned and unchecked.

## Workflow and ownership

Use project-workflow as the orchestrator and house planning-workflows as the lead. House planning-workflows, pstack Feature, and architect were inspected again for implementation. House planning fits the agreed module design and bounded diagnostics batch. Pstack technical-writing and unslop support the documents; verification-before-completion supports evidence. No full pstack Feature, architect, or delegated implementation run is claimed.

The user requested this GPT-6.1 Sol high-reasoning chat for batch 1. The previous planning chat finished its documentation before implementation began. This chat owns the coupled batch and shared implementation plan; no concurrent writer was used.

## Throughput and shared state

- Blocking first steps: read AGENTS, PRD, this feature, and the profile; inspect the working tree; keep frozen data unchanged. No classifier choice is needed for batch 1.
- Independent workstreams: later UI and audio experiments can separate only after shared types and contracts exist. No fan-out is needed for batch 1.
- Shared mutable state: one implementation owner writes model configuration, runtime contracts, and this plan. Inference runs get separate directories; gold stays read-only.
- Smallest safe decomposition: one owner for the coupled diagnostics, registry, and CLI slice. It can prove useful behavior without downloading a model.

## Verifiable batches

- [x] Batch 1: package, contracts, runtime health, and model registry. Create pyproject.toml, domain.py, models.py, ollama.py, cli.py, config/models.json, and focused tests. doctor reports the current server and empty-model status; models distinguishes configured from installed and compatible. No classifier default, model downloads, sign-in, inference, audio installation, or dashboard work. Update setup documentation and observed evidence.
- [x] Batch 2: selected text classifier. Owner selected qwen3.5:4b-q4_K_M before explicit provisioning. Implemented the accepted-policy prompt, structured response validation, provenance, exclusive run records, and classify CLI. Offline checks and focused development inference verified outcomes, evidence, identity, and failure behavior. See the execution record below; formal evaluation remains batch 3.
- [ ] Batch 3: text evaluation. Add development scoring and immutable prediction/report artifacts. Inspect mistakes on development only. Freeze a candidate system before an explicit held-out run; record the resulting limitations and D-004 decision separately.
- [ ] Batch 4: local transcription. Verify faster-whisper and CUDA dependencies in the project environment. Explicitly provision the planned turbo candidate, test a short fictional recording and silence, then expose small as a selectable fallback. Record elapsed time, memory behavior, model identity, and failures.
- [ ] Batch 5: dashboard. Add separate available-model selectors, text and audio forms, transcript editing, result details, reviewer decisions, case filters, and an evaluation summary. Bind locally. Demonstrate that widget reruns never trigger duplicate inference.
- [ ] Batch 6: paired audio and handoff. Run reference-text and audio-derived paths with a fixed classifier, inspect differences, verify GPU resource handoff, and update setup, diagrams, demo story, profile, and this plan.
- [ ] Review every acceptance criterion, record unrun checks and quality limitations, then move the feature to completed only when its agreed delivery scope is satisfied.

Each batch ends in a verified state before dependent work starts. If audio or UI grows substantially, split it into a separately numbered feature with explicit dependency and acceptance ownership.

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
| F-004-AC06 | 3 | python -m voice_callback.cli evaluate --split development --model MODEL_ID | Complete counts, failures, denominators, and inspectable predictions and scoring report. | Planned command; not implemented. |
| F-004-AC07 | 3 | Freeze candidate configuration, then run held-out evaluation once | Input-answer separation and configuration hash; tuning stops before run. | Not run. |
| F-004-AC08 and AC10 | 4 | python -m voice_callback.cli transcribe --input runtime/fixtures/fictional-call.wav --model large-v3-turbo | Full transcription completes, identity and measured timing recorded. | Planned command; fixture and runtime not provisioned. |
| F-004-AC04 and AC08 | 4 | Silent audio, corrupt file, oversized input, missing weights, and simulated GPU memory failure | Visible failure or established no-speech state; no fabricated callback decision. | Not run. |
| F-004-AC02 and AC09 | 5 | python -m streamlit run app.py --server.address 127.0.0.1 | Local dashboard with independent selectors, versioned edits, and separate reviewer decisions. | Planned command; app absent. |
| F-004-AC09 | 5 | Change a selector and unrelated widget, then explicitly submit twice | No automatic model run; each explicit submission has a distinct auditable result. | Not run. |
| F-004-AC10 | 6 | Compare paired audio and reference text with one fixed classifier | Separate transcription differences and decision changes; recorded memory handoff. | Not run. |
| Documentation | Each batch | git diff --check and local Markdown link inspection | No whitespace errors or broken changed-document links. | Batch 1: git diff --check passed. 146 local Markdown targets in 38 working documents passed; whitespace in all 14 untracked files passed. Bundled template assets excluded; see execution record. |

Use the project virtual environment. Batch 1 must document its editable installation command and supported Python version so package entrypoints are reproducible. Optional audio and dashboard dependencies remain separate from the first batch.

## Blockers and decisions

SRC-018 resolves the classifier choice and authorizes provisioning and development inference. The selected Qwen model is installed and exercised; formal evaluation remains batch 3. No application credentials are needed for the local plan. Batch 4 requires fictional audio fixtures and actual dependency verification. D-004 quality targets remain open; report results without inventing a pass threshold.

The proposed Streamlit UI, audio limits, and turbo setup are planning choices, not claims that they have passed hardware or product acceptance.

## Batch 1 pause and handoff (historical)

Current checkpoint: batch 1 implemented and verified in the project .venv. The feature is active and only batch 1 is checked. Frozen policy, candidates, approval, and gold remain unchanged. Existing documentation edits are preserved.
Next action: the owner chooses the callback classifier and exact local tag under D-003 before batch 2 can explicitly provision weights and run inference. No classifier is selected by this handoff. Confirm the Ollama executable path for that setup step; it is absent from this shell's PATH although the server is reachable.
Later batches remain unchecked. No audio/UI dependencies, model inference, model-quality results, cloud access, credentials, commit, push, or publication are part of this handoff.

## Completion and delivery

No overall application or model quality is accepted by this plan. Batch 2 explicitly downloaded the selected local classifier and ran development checks. No credentials or deployment were used. Final completion requires evidence against all ten acceptance criteria and clear reporting of the remaining quality decision. Merge, release, and deployment status remain unperformed.

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
