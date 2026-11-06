# F-005: Development quality baseline

Status: implemented and verified locally and in GitHub Actions on 2026-11-06. Owner: project owner.

Establish the quality gates requested on 2026-11-06 before F-004 batch 2. Model selection and inference remain outside this feature.

## Acceptance criteria

- F-005-AC01: pinned development dependencies provide Ruff lint/format checks and Pyright. Application source uses strict types; scripts and tests use standard types.
- F-005-AC02: one local command executes the same quality, behavior, immutable-data, documentation, and clean-package checks used by GitHub Actions.
- F-005-AC03: CI covers Ubuntu Python 3.10/3.13 and Windows Python 3.13, with bounded jobs, cancellation, read-only permissions, and no inference, model downloads, or stored build artifacts.
- F-005-AC04: pre-commit validates the staged snapshot; pre-push/review validates HEAD, with behavior checks proving dirty working files cannot substitute for the selected tree.
- F-005-AC05: the canonical project template requires explicit lint, formatter, type-check, behavior, and local/CI commands once the language is known. Generated-project validation catches missing requirements.
- F-005-AC06: setup/profile record exact commands, passing evidence, Free-account CI cost terms, and unavailable hosted or protection checks honestly.

Frozen policy, candidate source, approval, and gold are immutable. No account upgrade, billing change, hosted model, GPU job, credential provisioning, or paid branch protection is authorized.
