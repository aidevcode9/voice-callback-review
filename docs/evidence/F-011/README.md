# F-011 evaluation workflow verification

Date: 2026-11-08. Scope: engineering behavior of the local development workflow,
not model quality, held-out performance or deployment.

## Executable behavior

`tests/test_evaluation_integration.py` creates a disposable Git repository containing
the actual package, accepted policy bytes, model registry and two synthetic
development cases. A controlled loopback HTTP fixture returns predetermined model
responses. The real canonical CLI prepares a committed detached checkout and
executes its private worker. The test verifies exact revision/source/clean
provenance, progress, reports, a paired baseline fix, unchanged baseline bytes,
no expected-answer/secret markers in model calls, disabled SDK import, offline
review with zero HTTP calls, and dirty-source rejection before another inference.

Run from the project root with socket access:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p test_evaluation_integration.py -v
.venv\Scripts\python.exe -m unittest discover -s tests -p test_evaluation_review.py -v
.venv\Scripts\python.exe -m unittest discover -s tests -p test_evaluation_environment.py -v
.venv\Scripts\python.exe -m unittest discover -s tests -p test_evaluation_workflow.py -v
```

The desktop sandbox rejects controlled loopback connections with Windows error
10013. The integration and shared suite use the approved local socket execution
context; a sandbox connection failure is not an application pass. Existing CLI
tests now use per-test admission directories rather than the real workspace lock.

## Rendered browser acceptance

[Browser assertions](browser-acceptance.json) record the generated synthetic report
identities and actual browser results at 1440 and 390 pixels in light and dark.
The verified path covers a baseline with an unsafe miss and processing failure,
an improved run, paired changes, plain reports, case disclosure, exact transcript
and evidence, anchor navigation, keyboard focus, local table scrolling, no page
overflow, no remote resource requests and no transcript injection execution.

The Playwright check used the existing local Chromium headless shell and the web
workspace's installed Playwright. Four full-page captures and mobile detail crops
were inspected. Initial mobile headings wrapped excessively; minimum table widths
and internal horizontal scrolling resolved that defect without page overflow.
The report uses the Review desk's sage/forest palette and system text conventions.

PNG captures and synthetic run directories are local ignored artifacts. On this
workspace, `.test-work/f011-browser/fixtures.json` records the preserved plain and
comparison HTML paths; `docs/evidence/F-011` contains the captures. The local
browser check/capture scripts remain under `.test-work/f011-browser`. Reviewers on
another machine can run a development evaluation, open its printed report path,
and repeat the same viewport/disclosure/keyboard checks. No frozen cases were used
to create the browser fixtures.

Impeccable context, polish guidance and the craft floor informed the narrow repair.
Its mechanical scan reported only advisory typography/radius differences from the
app workbench. The standalone reading surface intentionally has a larger report
title, compact provenance text and section containers; no global token change or
sidecar regeneration is part of this feature. The existing design sidecar was
reported stale and was preserved.

## Evidence limits

Saved-snapshot review validates artifact bindings and versioned metric-count
consistency. It does not re-execute historical source or relax the original-source
guard on `score`. Unsupported pre-contract artifacts still require their original
source environment; they are not automatically migrated. Synthetic successes here
establish workflow correctness only. F-004's fresh model-quality baseline, owner
quality thresholds and explicitly authorized held-out check remain separate work.
