# Voice Callback Review workflow profile

Stage: owner-approved golden set v1.0 is frozen. F-004 is active with batches 1 and 2 diagnostics, contracts, and local text classification implemented. Evaluation, audio, and UI remain planned.

## Source of truth

The [brief](../intake/PROJECT_BRIEF.md) owns open decisions, the [PRD](../docs/PRD.md) owns proposed behavior, and the [source register](../intake/README.md) distinguishes user instructions from recommendations. Follow the shared [build process](../docs/HOW_WE_BUILD.md).

## Current skill choices

- Project orchestration: bundled [project-workflow](../.agents/skills/project-workflow/SKILL.md).
- Discovery support: installed `workflow-skill-manager`, using this project-specific profile.
- Lead for intake: bundled `project-intake`.
- Documentation: pstack `technical-writing` and `unslop`, read from the current installed environment.
- Review and handoff: `code-review-workflow`, `verification-before-completion`, and `branch-finish` when relevant.
- F-004 planning and batch 1: house `planning-workflows` selected after inspecting pstack Feature and architect. The agreed module design and coupled diagnostics slice use one implementation owner. Pstack technical-writing/unslop support documentation. No full pstack Feature, architect, or delegated implementation run is claimed. See the [active implementation plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) for actual execution.
- Later hard runtime bugs: consider pstack Bug fix when its required tools are available.

The intake and project-workflow skills are bundled. For every substantial task, inspect relevant pstack and house candidates, then record the choice and reason. See [workflow selection](../docs/WORKFLOW_SELECTION.md) for this stage's actual decisions. Other names describe this session's available skills, not portable installation guarantees. F-005 provides the configured snapshot preflight and shared local/CI runner described below.

## Validation at this stage

For documentation changes, inspect relative links, source claims, and diagram consistency with the written behavior, then run `git diff --check` for tracked edits and `git diff --cached --check` before commit. Structural validation of the bundled skill uses the installed skill-creator validator when available.

Batch 1 offline behavior and live runtime diagnostics are executable below. Model-quality, audio-quality, and UI checks remain unavailable until their owning batches. Do not treat a missing command or a successful diagnostic as successful inference.

## Data validation commands

- `python scripts/freeze_gold.py --check` verifies the frozen release, source/policy approval bindings, hashes, and exact exports.

- `python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl` validates structure and reports counts.
- `python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check` detects packet drift.
- `python -m unittest discover -s tests -v` exercises CLI behavior and the actual starter artifacts.

Run these for candidate data or tool changes. They do not validate semantic label correctness or human approval.

## Implemented batch 1 verification

Use [local setup](../docs/LOCAL_SETUP.md) to create .venv and install the package with the pinned build backend. Run repository commands from voice-callback-review. Python 3.10+ is supported; Python 3.13.1 was used for this batch.

| Surface | Exact command | Passing condition and observed result, 2026-11-05 |
| --- | --- | --- |
| Editable package | .venv\Scripts\python.exe -m pip install --disable-pip-version-check --no-deps -e . | Installed voice-callback-review 0.1.0 with no runtime dependencies. |
| Dependency consistency | .venv\Scripts\python.exe -m pip check | No broken requirements found. |
| Full offline behavior | .venv\Scripts\python.exe -m unittest discover -s tests -v | 49 tests passed: existing 22 plus 27 new behavior tests. No weights, Ollama server, or external network required. |
| HTTP and CLI behavior | .venv\Scripts\python.exe -m unittest discover -s tests -p test_ollama.py -v | Controlled loopback responses verify empty/populated inventory, refusal, timeout/deadline, HTTP/JSON/schema errors, response limits, local URL restrictions, and CLI exits. |
| Registry and domain behavior | .venv\Scripts\python.exe -m unittest discover -s tests -p test_models.py -v | Exact stage/tag matching, missing/unknown installation, incompatible/remote models, no default, immutable settings, and transcript hashing. |
| Runtime diagnostics | .venv\Scripts\python.exe -m voice_callback.cli doctor | Exit 0, Ollama 0.40.14 reachable, zero installed models, inference_verified false. Executable absent from this shell's PATH is reported separately. |
| Classification inventory | .venv\Scripts\python.exe -m voice_callback.cli models --stage classification | Exit 0 and no configured classifier; no implicit selection. |
| Transcription inventory | .venv\Scripts\python.exe -m voice_callback.cli models --stage transcription | Exit 0 and two planned candidates, both runtime_not_verified and not selectable. |
| Frozen data | .venv\Scripts\python.exe scripts/freeze_gold.py --check | Verified v1.0, 40 cases unchanged. |
| Source hygiene | git diff --check | No whitespace errors in tracked edits. Inspect new untracked source/config/docs as well before handoff. |

Diagnostic exit 1 indicates a request failure and unknown inventory is null. Exit 2 indicates configuration or argument errors. Zero models is an expected successful observation. Availability and configured capability never prove inference or quality. Local HTTP is read-only and bounded; no downloads, cloud fallbacks, or credentials.

## Later application verification

The classify command is implemented and the owner selected qwen3.5:4b-q4_K_M under SRC-018. See the [F-004 plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) for batch 2 offline and development-only live evidence. Evaluate, transcribe, and dashboard commands remain proposed. Keep batches 3 through 6 unchecked and F-004 active. Optional audio/UI dependencies are deferred until their versions and hardware behavior can be verified.

## Project invariants

- Candidate labels are not gold until reviewed under a stated rubric.
- Held-out expected labels do not enter classifier inputs.
- Transcription failures do not become no-callback decisions.
- Model output, reviewer decision, and the expected gold label stay distinguishable.
- A displayed evidence excerpt refers to the transcript version used.
- Configured and installed models are distinct; missing models never trigger a silent download or cloud fallback.
- Transcript edits and model changes preserve prior run provenance; selector changes alone do not invoke inference.
- Demo data is proposed to be fictional. No real customer source data has been supplied.

Product acceptance and model quality remain open. Preparing this PRD does not claim that an application is implemented or fit for operational use.

## Required engineering baseline (F-005)

Use [quality-gates.json](../quality-gates.json) as the explicit configuration record and [quality checks](../docs/QUALITY_CHECKS.md) for installation, execution, CI, and cost details. This section supersedes batch 1's earlier lack of static checks. The immutable-data and no-inference invariants remain in force.

- Install hash-pinned development tools with `.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.txt`, then install the project with `--no-deps --no-build-isolation -e .`. Runtime dependencies remain empty.
- Shared working-tree command: `.venv\Scripts\python.exe scripts/check_project.py`. It must pass lint, format, Pyright, behavior/coverage reporting, data, docs/lifecycle/workflow configuration, and clean-wheel installation. Named --suite options select the identical implementation used by CI.
- Before a commit: `.venv\Scripts\python.exe scripts/codex_preflight.py --mode pre-commit` validates the staged index. Stage the intended complete changes first. Untracked or unstaged files cannot satisfy the snapshot gate.
- Before push or committed review: `.venv\Scripts\python.exe scripts/codex_preflight.py --mode pre-push` or `--mode review` validates HEAD. Base branch is origin/main. The runner exports the exact selected tree and uses its source for subprocess imports. No separate preflight configuration file is required.
- Documentation-only changes may run `--suite docs` plus `git diff --check`; source/configuration/tool changes require the full baseline and matching snapshot preflight. Missing dependencies, commands, or nonzero checks block readiness.
- Ruff applies to first-party src/scripts/tests. Pyright is strict for src/voice_callback and standard for scripts/tests. No blanket type/lint suppressions are permitted to obtain a pass. Frozen data and bundled template assets stay outside automatic formatting.
- CI matrix: Ubuntu Python 3.10/3.13 and Windows Python 3.13. Quality/data/docs run once on Ubuntu. Hosted status must be reported separately from local results; live Ollama/inference/GPU checks are manual integration evidence.
- Owner reports GitHub Free. Current included compute is $12/month shared across eligible account usage. Remaining allowance and spending-stop settings are unverified. Private-repo protected branches are unavailable on this plan; no upgrade or billing changes are authorized. Hosted workflow activation is a separate delivery observation, never inferred from local YAML checks.

The template now requires explicit baseline configuration when the language is selected or source code appears. The bundled portable intake assets adopt that rule. Documentation-only intake with unknown language can defer tool choice without claiming application readiness.

## Branch and feature handoff policy

The owner requires a dedicated branch for every new feature or implementation batch before more code is pushed. Check git status and git branch --show-current before edits or publication. Use feature/<feature-id>-<short-name>; do not push feature work directly to main. Preserve existing unpublished commits instead of resetting them. Publish only the feature branch when authorized and use a pull request for review before merge. GitHub Free's private-repo protection limits do not waive this workflow.

The current F-004 batch 2 branch is feature/f-004-text-classifier. It starts from local c5cfdcd, which records F-005 completion and is not yet on origin/main. The remote baseline 8ab41a8 has four passing CI jobs. This branch carries the completion record and branch-policy handoff; no new push is performed by this setup. Classifier choice is still the owner's D-003 decision.

## F-004 batch 2 workflow and limits

Reassessed house planning-workflows, pstack Feature, and architect. House planning remains the lead for the existing classifier specification, with one implementation owner. Technical-writing/unslop, code-quality, error-handling, self-review, verification-before-completion, branch-finish, and the configured preflight support the batch. Systematic-debugging supports the observed context-error mapping correction. No full pstack playbook or delegated run is claimed.

The classifier uses exact input-only JSONL or UTF-8 text, a frozen policy hash, structured output validation, provenance, and exclusive runtime/classifications records. Model selection is explicit on every CLI request. Initial limits are 12000 transcript UTF-8 bytes, a 1 MiB input file, 8192 context tokens, 768 output tokens, and a 180-second inference deadline. Truncate and shift are disabled. Requires Ollama 0.40.15 or later for the inspected contract. Diagnostics retain their separate short deadlines.

Run the full shared baseline and matching snapshot gate for classifier changes, plus focused development-only live integration when model/runtime behavior changes. No live model or GPU run occurs in CI. Held-out scoring remains batch 3 after configuration freeze. No peak VRAM or production-quality result is inferred from successful local responses.
