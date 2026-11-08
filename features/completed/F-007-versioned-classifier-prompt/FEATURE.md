# F-007: Versioned classifier prompt asset

Owner and acceptance owner: project owner.
Status: functional implementation and verification complete, 2026-11-07. The final exact staged gate is required before the local completion commit.
Product requirements: F-004 classifier provenance and F-006 shared classifier behavior.
Dependencies: implemented callback-text-v2 classifier and F-005 package/snapshot gates.
Branch: codex/f-006-review-desk, explicitly retained at the owner's request.
Selected workflow: project-workflow orchestration with house planning-workflows as lead. Compared architect; the already agreed extraction does not need another design arena. Code-quality, focused behavior verification and branch-finish support this bounded change.

## Requirements

The owner agreed to move classifier instructions into a separate versioned file and add the change to this branch. Prompt content, accepted policy, schema, inference settings and stored history stay unchanged. No new model invocation, evaluation freeze, held-out execution, audio, UI redesign or publication is requested.

| Acceptance ID | Observable criterion |
| --- | --- |
| F-007-AC01 | The classifier reads its instructions from a Git-tracked package asset selected by the existing authoritative callback-text-v2 version identifier. |
| F-007-AC02 | The fully assembled system message and complete request remain byte/hash equivalent to the pre-extraction v2 baseline, including whitespace, policy and generated schema. |
| F-007-AC03 | A built/installed wheel can construct a classification request using the packaged prompt without importing repository source. |
| F-007-AC04 | Changing a prompt asset changes evaluation source identity, in addition to its rendered prompt hash. Existing records and frozen artifacts are preserved. |
| F-007-AC05 | Documentation identifies prompt ownership, the version-change procedure, package/source identity implications and the exact verification result. |

## Technical approach

Move only the static instruction prefix to src/voice_callback/prompts/callback-text-v2.txt. PROMPT_VERSION remains the single selector in classify.py; use importlib.resources to read its matching package file. Keep accepted policy loading separate and generate the response schema from contracts. No templating dependency or duplicate schema/manifest is needed for this one prompt.

Declare prompt text files as setuptools package data. Extend evaluation_config.source_identity to include prompt assets under relative paths alongside existing Python files. Include an installed-wheel request-construction smoke check. Source identity changes because code/assets change; this does not alter prompt meaning or authorize reuse of an earlier frozen code revision.

Before editing, captured an offline synthetic request from c0447dc. Its v2 system-message hash is fc0507692c9b15de6ee1cc928475f808c29723a3d6611d28b736c3e9f432e107. The fixed Unicode synthetic request hash is 14a8b592a577ae20dc29d411ca9f2abac6fdf932213a3f5d4811597363dc46d0. Regression checks compare these existing external request values, not a second implementation of the prompt.

## Implementation and verification

- [x] Extract instructions, include package data and fingerprint prompt assets.
- [x] Verify old rendered prompt/request hashes, asset-change identity and installed-wheel behavior.
- [x] Update living prompt/architecture docs and review the bounded diff.
- Required commit gate: scripts/codex_preflight.py --mode pre-commit must pass the final exact index; the completing commit records its observed outcome.

| Acceptance or check | Command/scenario | Observed result |
| --- | --- | --- |
| Pre-implementation baseline | scripts/check_quality_baseline.py | Passed; Python/TypeScript gates configured. |
| AC02 baseline | Offline build_classification_request with fixed synthetic Unicode input | Captured the v2 prompt and request hashes above; no runtime requests. |
| AC01/AC02 | Full behavior suite and fixed legacy request regression | All 116 tests passed before the final resource-error regression; full v2 prompt/request hashes unchanged. |
| Resource error | Focused classifier suite after safe prompt/policy read-error update | All 21 tests passed, including missing packaged prompt with zero network requests and no path disclosure. Final full-suite target is 117 tests. |
| AC03 | scripts/check_project.py --suite package | Passed: built wheel contains prompt and installed module constructs a request with PYTHONPATH removed; dependency/import/CLI checks also pass. |
| AC04 | Prompt-only asset change with unchanged Python/revision | Test passes; source_sha256 changes. Historical evaluation artifacts remain untouched. |
| AC05 | scripts/check_project.py --suite docs and git diff --check | Passed: 245 local links, lifecycle, OpenAPI and workflow checks. |
| Static gates | scripts/check_project.py --suite quality | Ruff, format and Pyright passed; final snapshot repeats them after the final small error-message change. |
| Independent review | Read-only package/provenance review versus c0447dc | No actionable findings. Reviewer independently extracted original AST string and verified all 665 bytes, including final LF LF, are identical; Python 3.10 compatibility checked by inspection. Reviewer did not run suites or inspect local user data. |

## Current state and completion

Known unrelated untracked .archify/ and .ua/ are preserved. The owner's local database, review and logs are not edited. The existing live API may need a restart after the local code update; no running user service is stopped automatically.

The extraction and acceptance criteria are verified locally; the final staged gate must pass before commit. No design deviation. PROMPT_VERSION selects a matching filename, keeping one authoritative version identifier without adding a duplicated manifest. The generated schema and governed policy remain separate. A safe configuration error now covers an unreadable prompt as well as the policy, with no runtime request.

The first staged whitespace check flagged the original instruction prefix's final blank line. A .gitattributes exception disables only blank-at-EOF detection for this exact v2 asset; its two LF separator bytes are preserved, and other whitespace checks stay enabled. No rendered prompt normalization was introduced.

Final matching snapshot validation is recorded in the completing commit message. No live inference, model-quality measurement, evaluation freeze, held-out access or stored-review change was performed. Merge/deployment/release remain outside this local branch change. The existing running backend was left alone; restart it to use the updated builder. The source identity change requires a fresh committed development baseline before a future candidate freeze; prior frozen artifacts are not rewritten.
