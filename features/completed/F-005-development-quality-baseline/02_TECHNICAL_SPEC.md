# F-005: Quality baseline design

## Execution

Use pinned requirements-dev.txt in the existing .venv. Ruff checks first-party src, scripts, and tests. Pyright is standard for the same paths and strict for src/voice_callback. Vendored template assets and frozen data are not reformatted.

scripts/check_project.py --suite all is the shared runner. Named suites quality, tests, data, docs, and package allow CI jobs to call the same implementation. Failures stop the selected suite. Documentation checks inspect working Markdown targets and feature folder structure. Package checks build a wheel, install it in a disposable environment, and verify CLI/help imports without the editable source on PYTHONPATH.

scripts/codex_preflight.py exports the index for pre-commit and HEAD for pre-push/review into bounded scratch space, then runs the snapshot's checker with its src on PYTHONPATH. Exported paths and temporary roots are checked. Snapshot tests and clean-wheel checks prove the real artifact rather than the current dirty directory.

.github/workflows/ci.yml runs a single quality/data/docs job and a three-entry behavior/package matrix. It uses immutable action revisions, read-only contents permission, timeout limits, and concurrency cancellation. Push-to-main, pull-request, and manual triggers avoid duplicate branch-push/PR runs. No artifact upload is needed.

The generic template gains explicit quality-gate fields and a validator; unknown tools can remain unresolved during documentation-only intake, but source implementation cannot silently skip lint/format/types. Python guidance recommends Ruff/Pyright, and other languages choose equivalent tools.

## Cost and delivery

The owner reports GitHub Free. Current official documentation includes $12/month compute, with standard Linux x64 at $0.006/minute and Windows x64 at $0.010/minute; all eligible account usage shares that allowance. No remaining usage or hard budget could be verified through the current credentials. Do not promise zero charges. Private-repo protected branches require an eligible paid plan. Prepare/test locally before activating hosted work; do not change account billing.
