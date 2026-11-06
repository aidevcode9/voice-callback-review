# Run project quality checks

Use the project virtual environment and Python 3.10 or later. Pyright also needs Node; local Node is already available, and CI selects Node 22 for the quality job.

## Install the development tools

```powershell
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.txt
.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
```

The requirements pin Ruff, Pyright, build tools, coverage, YAML parsing, and transitive dependencies with release hashes. Python/OS markers include conditional build dependencies. Coverage 7.10.7 supports the declared Python 3.10 minimum; development tools remain separate from runtime dependencies. Update pins and their PyPI release hashes together and rerun the minimum-runtime CI job.

## Run the same checks as CI

```powershell
.venv\Scripts\python.exe scripts/check_project.py
```

The default runs quality, tests, data, docs, and package suites. Use --suite with one of those names for a focused check. Every nonzero result blocks the selected suite.

Quality includes Ruff correctness/import rules, formatting checks, and Pyright. Application source uses strict types; scripts and tests use standard checking. Tests retain unittest and report application branch coverage without an invented percentage threshold. The coverage report covers the parent test process; child CLI processes are verified by their tests but are not added to that report.

Data checks validate the frozen release and unchanged candidate packet. Docs check local links, feature lifecycle, explicit quality configuration, and workflow structure/action pins. Package checks build a wheel with the pinned backend, install it without dependency downloads in a disposable environment, verify imports come from that installation, and run both CLI help entrypoints. No model weights or inference are needed.

Automatic formatting covers src, scripts, and tests. Bundled template assets, gold, policy, candidate source, and approval are preserved. Development scratch, coverage, wheels, and environments stay under ignored paths. On this managed desktop, controlled loopback tests need a shell with local socket access; PermissionError 10013 indicates a sandbox restriction and is not evidence that the application passed.

## Validate the artifact being handed off

```powershell
.venv\Scripts\python.exe scripts/codex_preflight.py --mode pre-commit
.venv\Scripts\python.exe scripts/codex_preflight.py --mode review
.venv\Scripts\python.exe scripts/codex_preflight.py --mode pre-push
```

Pre-commit exports the staged index. Review and pre-push export HEAD. Stage or commit the complete intended source first. A passing dirty-working-tree check cannot replace these snapshot checks. The selected tree must include the checker, workflow, metadata, and every source/test file it needs. Subprocess imports use the exported source; the wheel smoke test uses a fresh installation with PYTHONPATH removed.

## GitHub Actions and cost

[ci.yml](../.github/workflows/ci.yml) runs on pull requests, pushes to main, and manual dispatch. It has one Ubuntu quality/data/docs job and tests/package jobs on Ubuntu Python 3.10/3.13 and Windows Python 3.13. Jobs have eight-minute timeouts, read-only contents permission, immutable action pins, and cancellation of superseded runs. Branch pushes do not duplicate pull-request workflows. Build artifacts are not uploaded or retained. No GPU or model provisioning job exists.

The owner reports GitHub Free. As checked on 2026-11-06, Free includes $12/month of compute shared across eligible account usage, plus 500 MB artifact storage. Standard Linux x64 is $0.006/minute and Windows x64 $0.010/minute, rounded up per job. Usage beyond the included amount can be billed. Local checks have no GitHub Actions charge. Remaining allowance, payment method, and a spending-stop budget were not accessible through the current GitHub credentials. Do not infer that all CI usage will be free.

Check [GitHub billing](https://github.com/settings/billing) for account usage and spending controls. The repository cannot enforce the account billing limit through YAML. Configure a budget with Stop usage enabled if a hard cap is desired. No account or billing settings are changed by this feature.

GitHub Free supports these workflows, but protected branches for this private repository require an eligible paid plan. The local/snapshot gates and CI status can be used on Free; server-side mandatory merge checks are not claimed or configured.

Official references: [included usage](https://docs.github.com/en/billing/reference/product-usage-included), [runner rates](https://docs.github.com/en/billing/reference/actions-runner-pricing), [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), and [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
