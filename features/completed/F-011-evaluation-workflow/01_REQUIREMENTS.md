# F-011: Coherent evaluation workflow

Owner and acceptance owner: the user. Product requirements: PRD-R007 and PRD-R008.
Source: SRC-025 in the [source register](../../../intake/README.md), the 2026-11-08 conversation requesting a first-class evaluation workflow,
conventional local configuration, a dedicated branch, and implementation through
the project workflow. Dependencies: F-004 evaluation core and F-009 optional tracing.

## Problem, users, and outcome

The evaluator already runs inference and scoring together, but operators coordinate
a traced-only launcher, raw JSON reports, and separate commands. The owner needs
one reproducible development workflow that answers what happened and what changed.

## Scope and exclusions

Deliver a canonical packaged development entry point, optional tracing, local
`.env` loading, visible progress, readable saved-run reports and compatible baseline
comparison. Reuse the classifier, scorer, immutable records and model registry.
Preserve the existing rescore and candidate-freeze operations as deliberate actions.
The owner selected one command plus a local browser report in the asynchronous
interface question on 2026-11-08. An in-app evaluation area remains a later extension.

No new model, label changes, inferred quality threshold, automatic candidate freeze,
held-out inference, deployment, or external tracing request is part of verification.
The frozen dataset and original quality evidence remain unchanged. A YAML profile
is unnecessary for the current single-model selection; keep `config/models.json`.

## Acceptance criteria

| Acceptance ID | Observable outcome | Boundary or failure case |
| --- | --- | --- |
| F-011-AC01 | One documented command prepares the current committed implementation and runs the development split with the shared inference lock. | Relevant dirty source/config/data is rejected before inference; no stale checkout is silently evaluated. |
| F-011-AC02 | Root `.env` supplies supported tracing settings; process environment takes precedence; `.env.example` contains placeholders. | Secrets never enter output, reports, argv, or tracked files; tracing is optional and cannot prevent untraced evaluation. |
| F-011-AC03 | Progress identifies completed cases; interrupted runs retain an inspectable location and recovery instructions. | No complete quality report is produced for interrupted or uncertain provider execution. |
| F-011-AC04 | A local readable report displays metrics with counts, confusion matrix, failures, unsafe misses, provenance and case-level expected/predicted decisions with evidence. | Text is escaped; undefined metrics remain undefined; execution success is distinct from quality acceptance. |
| F-011-AC05 | An explicit baseline produces compatible metric and case changes, including fixes and regressions. | Reject different dataset/split/input/answer/scorer definitions; allow model/prompt/source changes; never rewrite or rescore an old baseline under different source. |
| F-011-AC06 | Prior completed runs can be listed and reviewed without inference or telemetry. | Reject incomplete/tampered runs and retain earlier artifacts. Held-out material is excluded from the development workflow. |
| F-011-AC07 | Documentation, current/proposed flow diagrams and verification match the delivered interface. | Model quality, owner acceptance, commit/merge and deployment remain distinct. |

## Open product decisions

The interface preference was requested asynchronously on 2026-11-08. The owner
selected the recommended command-plus-browser-report first slice. An in-app
Evaluations area would expand API/job/frontend acceptance. Numeric quality targets remain open
under D-004 and do not block implementing evaluation tooling.

- [Technical specification](02_TECHNICAL_SPEC.md).
- [Implementation plan](03_IMPLEMENTATION_PLAN.md).
