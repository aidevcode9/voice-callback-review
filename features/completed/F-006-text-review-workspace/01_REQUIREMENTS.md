# F-006: Text review workspace requirements

Owner and acceptance owner: project owner.
Status: completed functional implementation and verification, 2026-11-07, under SRC-021/SRC-022. Merge, live model-quality acceptance, final audio and deployment remain separate.
Product requirements: PRD-R002, R004, R005, R008 through R012.
Sources: SRC-020 through SRC-022 in the [source register](../../../intake/README.md).
Dependencies: F-004 diagnostics/classifier/contracts and saved-run provenance; completed F-005 engineering baseline. Classifier PR #1 and evaluation/contracts PR #2 are merged. This branch was fast-forwarded to main c82f0ed before design continued; no code-tree differences from 18f8677.

## Problem, users, and outcome

The owner needs a polished local workspace for testing fictional text conversations and showing senior engineers how evidence, model output, human review, and provenance stay distinguishable. A service reviewer remains a proposed persona. This is its own substantial feature because frontend state, API jobs, case persistence, and browser acceptance have distinct outcomes from the inference core.

## Scope and exclusions

Two rendered directions were reviewed; the owner selected A Review desk and authorized implementation. Next.js is the approved frontend direction with Nginx and a thin proposed FastAPI API over the existing Python core. The selected A Next.js workspace, FastAPI/SQLite backend and Nginx single-origin routing are implemented and functionally verified. Text review and testing precede audio. Hosting is undecided; deployment is excluded.

Include pasted text, fictional development examples, explicit model selection and classification, versioned editing, exact quote highlights, recommendation/rule/reason, separate human review, immutable run history, provenance disclosure, compact case navigation, outcome and review filters, and meaningful processing states. No confidence score, invented quality dashboard, batch inference, multi-user queue, model downloads, credentials, automatic retries, automatic dialing, gold relabeling, or held-out browsing.

Prototype fixtures are newly authored fictional examples, not frozen cases or measured model outputs. The iterative API may load input-only development examples; it never offers held-out cases or expected answers. Formal evaluation and candidate freeze remain F-004 CLI responsibilities. A future report viewer may display a development report with source/version labels; it must not become a held-out tuning loop.

## Acceptance criteria

| ID | Observable outcome | Boundary or failure case |
| --- | --- | --- |
| F-006-AC01 | Two browser-renderable directions show the same truthful workflow at desktop and narrow widths, with evidence and tradeoffs. | Simulated output and processing are plainly labeled; neither is represented as the production application. |
| F-006-AC02 | Paste text or explicitly load a fictional development case; choose an available classifier, then submit. | No inference on selector/filter/navigation/edit/reload changes. One accepted job per explicit action; repeated delivery of the same submission cannot duplicate it. |
| F-006-AC03 | A submitted run binds an immutable transcript version and explicit model configuration; text edits create a new version. | Earlier results retain original text, quotes, model/settings, hashes, and status after edits, new runs, or reload. Unsaved edits cannot be submitted. |
| F-006-AC04 | Successful output shows outcome, accepted policy rule, reason, and exact highlighted supporting quote(s). | Evidence is highlighted only against the selected run's transcript; ambiguous duplicate occurrences have a defined display convention. A failure has no policy label. |
| F-006-AC05 | Save a human decision and note separately for a named run/version. | Disagreement never overwrites model output, expected answers, approved policy, or gold. Prior review events remain inspectable. |
| F-006-AC06 | Empty, running, timeout, malformed-output, unavailable-runtime, input-limit, busy and interrupted states offer an explicit next action. | Navigating or disconnecting cannot create a false no-callback result, hide earlier runs, or start a retry. |
| F-006-AC07 | Run history survives backend/browser restart and exposes technical provenance on demand. | Selected input version, model identity/configuration, prompt/policy/source identity, timing, and failure cause remain distinguishable; unknown values are identified. |
| F-006-AC08 | Nginx serves one browser origin with pages/assets to Next.js and /api to Python; API delegates inference and validation to the core. | FastAPI and Ollama are loopback-only; reject foreign-origin writes, oversized requests, unexpected fields and stale versions. No second prompt/scorer or arbitrary file-path API. |
| F-006-AC09 | Keyboard, focus, labels, meaningful status text and outcome colors support review at 1440px and 390px, including long text. | No clipped primary actions, horizontal document overflow, color-only status, or inaccessible error recovery. |
| F-006-AC10 | The API enforces one active inference job and bounded resource use independently of browser controls. | Concurrent tab/CLI contention, double submission, crash recovery and idempotent retries are tested before live integration. No silent model provisioning. |

AC01 is the design deliverable. AC02–AC10 have production-stack browser/API evidence mapped in the implementation plan; the controlled Ollama fixture proves integration behavior, not semantic model quality. [F-004](../../active/F-004-local-model-pipeline/01_REQUIREMENTS.md) retains core diagnostics, quality, transcription, and paired-audio acceptance. F-004-AC09 UI ownership transfers here to AC03/AC05; F-004-AC02 retains independent model capability/availability, with selector behavior owned here and final transcription integration in F-004.

## Open decisions

Resolved: owner chose A Review desk and authorized implementation under SRC-021. SRC-022 directed completion. API/storage/resource boundaries and production browser behavior have observed verification. D-004 numeric model-quality targets and D-005 hosting remain open outside this local feature; no operational fitness or deployment is accepted here.

## Related documents

- [Technical specification](02_TECHNICAL_SPEC.md).
- [Implementation plan and evidence](03_IMPLEMENTATION_PLAN.md).
- [Design comparison](../../../prototypes/text-review/index.html).
