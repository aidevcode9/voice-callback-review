# F-009: Implementation plan

## Workflow and checkpoints

House planning-workflows leads: the request spans integration, credentials, documentation and a cost model. The project-workflow and Langfuse instrumentation skills guide the design; architect was considered but its multi-candidate arena is disproportionate to a bounded instrumentation boundary. The spreadsheet skill guides the worksheet. One implementation owner handles shared code and documents.

- [x] Verify dedicated branch and baseline configuration.
- [x] Add opt-in tracing and optional, reproducible dependency setup; verify behavior and privacy.
- [x] Create and verify TCO workbook with editable assumptions.
- [x] Run working-tree project checks and review the changed behavior.
- [ ] Run the staged snapshot gate as part of a later branch handoff.

## Evidence and delivery

Baseline configuration passed `python scripts/check_quality_baseline.py`. Feature branch: `feature/f-009-langfuse-tco`. The user's credentials file remains local and is ignored. Langfuse authentication succeeded; a synthetic run's retrieved observation tree contained a parent span and nested generation with 100 input and 20 output tokens, with content omitted. No held-out data was used. The workbook was rendered and its formula results checked with a known input set and missing-input case; native Excel recalculation was not exercised.

The shared runner passed Python quality, 122 behavior tests, data, docs, package, frontend lint, types, and build. Its browser step initially failed because the default Playwright Chromium was missing. The five browser tests passed separately using the existing Chromium via `CHROMIUM_EXECUTABLE`, with the same controlled stack. The docs suite passed again after the architecture update. Staged snapshot preflight, hosted CI, independent acceptance, merge, and deployment remain pending.
