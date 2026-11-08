# F-009: Implementation plan

## Workflow and checkpoints

House planning-workflows leads: the request spans integration, credentials, documentation and a cost model. The project-workflow and Langfuse instrumentation skills guide the design; architect was considered but its multi-candidate arena is disproportionate to a bounded instrumentation boundary. The spreadsheet skill guides the worksheet. One implementation owner handles shared code and documents.

- [x] Verify dedicated branch and baseline configuration.
- [x] Add opt-in tracing and optional, reproducible dependency setup; verify behavior and privacy.
- [x] Create and verify TCO workbook with editable assumptions.
- [x] Run working-tree project checks and review the changed behavior.
- [x] Run staged and committed snapshot gates for the original tracing and worksheet handoff.

## Evidence and delivery

2026-11-07 evaluation tracing: the owner requested Langfuse traces for `evaluate`. The shared classifier emits one trace per case with evaluation ID, split, dataset version, and case ID; reference answers and scoring remain local. The normal content switch and held-out authorization and freeze gates remain in effect. A two-case fictional fixture used predetermined fake model responses to verify transport; it did not measure the model. Its original D2 trace was inconsistent because it paired an outstanding callback request with a no-callback response. The fixture now explicitly withdraws the request and uses supporting evidence. The earlier traces remain in Langfuse as historical test data. No real gold inputs or held-out cases were used in that transport test. Project checks and real development inference remain pending.

2026-11-07 correction: the owner requested useful trace input and output. The original metadata-only default is replaced with transcript and validated decision capture when tracing is enabled; `VCR_LANGFUSE_CONTENT=0` retains metadata-only behavior. This deliberately sends potentially sensitive call content to the configured Langfuse instance. Focused tests passed for both modes. An authenticated fictional fixture trace was fetched from Langfuse: its parent and generation contained the transcript and validated label, rule, reason and evidence, with 100 input and 20 output tokens. No held-out data was used. The follow-up PR records its own snapshot and hosted checks.

Baseline configuration passed `python scripts/check_quality_baseline.py`. Feature branch: `feature/f-009-langfuse-tco`. The user's credentials file remains local and is ignored. Langfuse authentication succeeded; a synthetic run's retrieved observation tree contained a parent span and nested generation with 100 input and 20 output tokens, with content omitted. No held-out data was used. The workbook was rendered and its formula results checked with a known input set and missing-input case; native Excel recalculation was not exercised.

The shared runner passed Python quality, 122 behavior tests, data, docs, package, frontend lint, types, and build. Its browser step initially failed because the default Playwright Chromium was missing. The five browser tests passed separately using the existing Chromium via `CHROMIUM_EXECUTABLE`, with the same controlled stack. Staged and committed snapshot gates subsequently passed with that browser. The original tracing and worksheet changes merged through PR #4. Product acceptance and deployment remain separate.
