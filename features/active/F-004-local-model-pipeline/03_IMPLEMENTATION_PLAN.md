# F-004: Local model pipeline implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).
Status: active. Batch 1 is implemented and verified; batches 2 through 6 remain planned and unchecked.

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
- [ ] Batch 2: selected text classifier. Resolve the deferred owner choice before download. Add an explicit setup step for the chosen local model, the accepted-policy prompt, structured response validation, and a classify command. Verify one fictional development input and error behavior; record exact model identity and settings.
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
| F-004-AC03 through AC05 | 2 | python -m voice_callback.cli classify --input data/gold/v1.0/inputs/development.jsonl --case-id VC-001 --model MODEL_ID | Valid result or explicit failure with provenance. | Planned command and arguments; not implemented. |
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

The owner deferred classifier selection. It blocks batch 2's real model download and inference, not batch 1. No application credentials are needed for the local plan. Batch 4 requires fictional audio fixtures and actual dependency verification. D-004 quality targets remain open; report results without inventing a pass threshold.

The proposed Streamlit UI, audio limits, and turbo setup are planning choices, not claims that they have passed hardware or product acceptance.

## Pause and handoff

Current checkpoint: batch 1 implemented and verified in the project .venv. The feature is active and only batch 1 is checked. Frozen policy, candidates, approval, and gold remain unchanged. Existing documentation edits are preserved.
Next action: the owner chooses the callback classifier and exact local tag under D-003 before batch 2 can explicitly provision weights and run inference. No classifier is selected by this handoff. Confirm the Ollama executable path for that setup step; it is absent from this shell's PATH although the server is reachable.
Later batches remain unchecked. No audio/UI dependencies, model inference, model-quality results, cloud access, credentials, commit, push, or publication are part of this handoff.

## Completion and delivery

No application or model quality is accepted by this plan. No models were downloaded, no credentials were used, and no deployment was performed. Final completion requires evidence against all ten acceptance criteria and clear reporting of the remaining quality decision. Merge, release, and deployment status remain unperformed.

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
