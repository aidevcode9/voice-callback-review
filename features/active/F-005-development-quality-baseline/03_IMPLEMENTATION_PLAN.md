# F-005: Quality baseline implementation

Status: local implementation verified; staged-snapshot and hosted delivery checks remain to be recorded.

Lead workflow: house planning-workflows, after re-reading project-workflow and inspecting pstack Feature. One owner handles coupled tool configuration, source typing, shared runner, and CI. Pstack Feature's delegated design/implementation is not selected or claimed. Build-the-lever supports the rerunnable checker; code-quality and verification-before-completion support implementation and handoff.

## Checkpoints

- [x] Inspect clean Git trees in voice-callback-review and project-template; read project instructions and relevant source.
- [x] Verify official tool releases, immutable action revisions, and GitHub Free cost/protection limits.
- [x] Pin development tools and configure lint/format/type checks; resolve actual findings without blanket exclusions.
- [x] Add shared suites, clean-wheel checks, snapshot preflight, and focused failure-path tests.
- [x] Add bounded GitHub Actions workflow and canonical-template quality requirements with generated-project regression checks.
- [ ] Run local checks, immutable-data verification, template validation, self-review, and document actual evidence and delivery state.

Blocking steps: existing instructions/status and frozen invariants checked first. Independent workstreams: none delegated; template checks are separate commands after edits. Shared state: one owner writes the profile and runners. Smallest decomposition: one owner prevents config, type, and CI command drift.

No F-004 classifier decision is made. Later F-004 batches remain unchecked. Hosted runs, commits, pushes, and branch protection are not claimed by local validation.

## Local execution evidence, 2026-11-06

- Installed pinned Ruff 0.17.4, Pyright 1.1.414, build 1.6.1, coverage 7.10.7 (Python 3.10-compatible), PyYAML 6.0.3, setuptools 80.9.0, and fully pinned/hash-verified transitive development dependencies. Conditional markers cover Python 3.10 and Windows requirements. Application runtime dependencies remain empty.
- Initial lint identified 13 issues, and Pyright identified 54 diagnostics. Safe lint fixes and first-party formatting were applied. JSON boundaries now use explicit recursive JSON types and scalar validation; doctor keeps its two result types separate. No blanket suppressions or first-party exclusions were introduced.
- scripts/check_project.py passed the complete working-tree baseline: pinned-tool/dependency consistency, Ruff check, Ruff format --check, Pyright with zero errors/warnings, all 55 unittest cases, three immutable-data checks, 154 document links plus lifecycle/workflow checks, wheel build, fresh isolated installation, import-origin assertion, and both CLI help entrypoints.
- Six new gate tests cover subprocess failures, missing links, duplicate feature IDs, mutable action references, missing CI quality suite, and staged/HEAD exports that exclude dirty/untracked replacement content.
- An initial restricted-shell test run failed with Windows socket PermissionError 10013. A trace established a sandbox boundary; the same complete suite passed with controlled loopback access. A separate staged fixture exposed Windows newline translation; the fixture now writes exact LF bytes before Git whitespace checking.
- Canonical project-template: python -m unittest discover -s tests -v ran 14 tests with one environment-dependent symlink skip; other checks passed. python scripts/validate_template.py verified the generated self-contained project and 80 document links. Its regression cases reject missing gates once language/code exists while allowing unknown-language documentation intake. Portable intake assets in this app adopt the template changes.
- Frozen policy, candidates, approval, and gold compare unchanged with Git. No classifier selection, model download/inference, audio/UI dependency, API key, or billing/account change occurred.

GitHub Free was supplied by the owner. Read-only APIs could not retrieve plan/usage or budget state with current scopes. Official current docs report $12/month included compute and standard Linux/Windows rates of $0.006/$0.010 per rounded job-minute. The four configured jobs have eight-minute limits, cancel superseded runs, and upload no artifacts. Private protected branches are unavailable on this plan. Hosted results cannot be inferred from local validation.
