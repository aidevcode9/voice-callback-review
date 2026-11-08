# F-006 functional verification

Date: 2026-11-07. Scope: built production Next.js A Review desk, actual loopback Nginx routing, FastAPI and SQLite. Ollama HTTP responses are controlled fictional fixtures; no live model inference, semantic quality score, held-out access, audio or deployment is claimed.

Run `python scripts/check_project.py --suite web` after the explicit tooling setup in [local setup](../../LOCAL_SETUP.md#browser-verification). The suite checks locked dependencies, generated contracts, Biome, TypeScript, production build and five Playwright flows. It owns isolated ports/database/processes and counts controlled classifier HTTP requests. Browser screenshots are captured by the test from its production build, from the top of the page, at 1440×1000 and 390×844 viewports. They are generated local verification artifacts and are ignored by Git; rerun the suite to regenerate them. The written record and assertions remain tracked.

| Evidence | What it shows |
| --- | --- |
| Empty desk (`empty-desktop.png`, local capture) | First action, explicit text/example input and model selection. |
| Desktop (`review-desk-desktop.png`, local capture), narrow (`review-desk-narrow.png`, local capture) | Exact repeated/overlapping quote highlights, model recommendation, separate human disagreement and history. |
| Processing with history (`loading-with-history.png`, local capture) | Earlier transcript/result remains inspectable while a new version processes. |
| Malformed output (`malformed-output.png`, local capture) | Processing failure without a policy label; original runs retained. |
| Unavailable runtime (`runtime-unavailable.png`, local capture) | Prior result remains visible with explicit reconnect guidance. |
| Timeout/recovery (`timeout-recovery.png`, local capture) | Failed run and recovery admission; no automatic retry. |
| Preserved provenance (`preserved-provenance.png`, local capture) | Earlier version, human decision and model/source identity survive API restart. |
| Input limit (`input-limit.png`, local capture), Unicode/long line (`unicode-long-narrow.png`, local capture) | UTF-8 byte limit and exact text with narrow layout wrapping. |
| Interrupted worker (`interrupted.png`, local capture) | Explicit interruption, no fabricated policy outcome and manual recovery. |
| [Assertion summary](browser-evidence.json) | First flow's request count, one-origin observations and desktop/narrow axe results. |
| [Finish review](REVIEW.md) | Independent visual finding and resolved verdict. |

The first browser flow checks explicit submission, zero inference from filters/selectors/edit/review/reload, immutable v1/v2 input and evidence, second-tab contention, lost-response reconciliation, runtime failure handling and restart persistence. Axe WCAG 2 A/AA and 2.1 AA scans report zero violations at both widths; rendered captures were also inspected. The second flow covers keyboard entry/save focus, UTF-8 limits, recoverable save failure, long Unicode input, interrupted work, explicit example loading, keyboard review/provenance and malformed API-response recovery. Automated accessibility is bounded evidence, not a universal accessibility certification.

The API suite additionally exercises same-key replay, stale parent conflicts, append-only review corrections and pagination, immutable SQL history, API/CLI contention, crash/recovery ordering, unsafe origins/nonce/fields/body limits and storage failures. Existing core tests cover context limits, model availability, output validation and safe error semantics. Frozen policy/candidates/approval/gold are checked unchanged.

Local evidence uses Windows Python 3.13, Node 22.12, Nginx 1.31.8 and an explicitly selected cached Chromium headless shell. The Linux hosted CI job is configured to invoke the same suite but has not run for this unpublished branch. Normal startup uses actual local Ollama and has no controlled-response banner. No real-model run was performed for F-006; model-quality acceptance remains F-004 work.

The three F-008 reliability flows additionally cover disabled editing during a pending save, reconnect preserving the current case draft, and completion of one case while another job is running. They drive the production frontend with fictional intercepted API responses; the original two flows still use the actual local Nginx/FastAPI/SQLite stack with its controlled Ollama fixture. No screenshots are required in a clean checkout.
