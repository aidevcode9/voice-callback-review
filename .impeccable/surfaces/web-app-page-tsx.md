---
version: 1
slug: "web-app-page-tsx"
primary_target: "web/app/page.tsx"
related_targets: ["web/app/globals.css", "web/app/components.tsx", "web/lib/use-workspace.ts"]
---

# Production Review desk surface

Mode: Operate. Owner-selected A, SRC-021; completion authorized in SRC-022. Extends the approved prototype world, without a new identity workshop.

## Direction contract

THESIS: Keep the transcript and human judgment adjacent; saved versions and earlier model output remain inspectable during new work.

OWN-WORLD: Sage case rail, white reading surface, forest primary action, system sans, amber exact evidence marks and distinct named outcome colors. Familiar labeled controls and disclosures.

STORY: Paste/load fictional text, explicitly save and select a model, submit once, read evidence/rule/reason, append separate human review, and inspect prior versions/runs. Processing failure is not a policy outcome.

FIRST VIEWPORT: 235px case rail, compact case header, flexible transcript and 330px decision column; submit under saved text, history/provenance below. At 390px the rail becomes horizontal navigation and the work areas stack without clipped actions. Empty state explains the first action. Controlled verification is labeled; ordinary operation shows actual runtime state.

FORM: Selected grounded candidate 1 from the approved prototype exploration; seed:15bb05bc61674be4. Production Next.js uses the actual API through one local Nginx origin. Signature interaction restores a selected earlier run's exact transcript/evidence while retaining the newest version for explicit submission.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Verification

Drive actual Next.js/Nginx/FastAPI with controlled Ollama HTTP responses. Verify no inference from selectors/navigation/edit/reload; explicit idempotent submission, lost-response reconciliation, errors, separate decisions, earlier evidence and restart persistence. Capture desktop/narrow states, run keyboard/accessibility checks and inspect rendered output. No held-out inputs/answers, model downloads, live quality evaluation, audio or deployment.


## Implemented surface and finish status

The production frontend is implemented in `web/app/page.tsx`, with recommendation, exact-evidence, human-review and provenance components in `web/app/components.tsx`, styling in `web/app/globals.css`, and workspace interaction state in `web/lib/use-workspace.ts`. It extends approved A; B Casebook remains historical comparison evidence. No new visual world or shared token-system change was introduced by this documentation pass.

The implemented desktop composition retains the sage rail and adjacent reading/decision areas. At the narrow breakpoint, filters wrap, cases scroll horizontally, navigation actions fill the width and transcript, recommendation, review and history stack. Exact quote marks follow the selected run's saved transcript; the classifier action explicitly submits the latest saved version. Human review is presented as a separate record. Runtime failure, uncertain submission acceptance and active processing have separate notices.

Finish reviewer verdict: **pass — ship the frontend** after the initial stale processing notice finding was resolved. The original finding is closed. This records the finish review outcome supplied for this pass; it is not a claim of merge, deployment, live-model quality or application acceptance.

## Evidence checked

- Read `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, `docs/REVIEW_DESK_SURFACE.md`, `web/app/globals.css`, `web/app/page.tsx` and `web/app/components.tsx`.
- Visually inspected `docs/evidence/F-006/review-desk-desktop.png` and `review-desk-narrow.png`. They show the selected A palette, exact amber evidence, separate human decision and preserved run history; the narrow capture has no clipped primary action.
- Read `docs/evidence/F-006/browser-evidence.json`: it records Next.js/Nginx/FastAPI verification with controlled Ollama HTTP responses, one local API origin and zero recorded desktop/narrow axe violations. Its assertion list includes explicit submission, selector/edit/review/reload inactivity, persistence, contention, lost-response reconciliation, runtime failures and restart. These are recorded verification results, not tests rerun by this documentation pass.
- Captures label controlled fictional responses and explicitly exclude model inference. They support interface review, not numeric quality acceptance.

## Observed token and preview drift

Preserve the incumbent frontmatter tokens and sidecar extension/component fields. The following source differences are visible and remain unmodified:

- Production transcript text is pre-wrapped inline content at line height `1.9`; the retained transcript token and prototype speaker-row treatment use `1.7`. The sidecar reading preview still illustrates the historical speaker-row layout.
- Production progress uses a `35%` segment translated to `400%`; the sidecar motion record and prototype use a `40%` segment translated to `350%`, both over `1.6s ease-in-out`.
- Production inputs/selects have a `40px` minimum height; the sidecar field preview retains `39px`. Production narrow buttons have a `44px` minimum height.

The palette, font stack, radii and principal A column dimensions remain aligned with the approved world. Historical B tokens and prototype snippets remain for reproduction and comparison, not as production behavior specifications. Future token reconciliation should be a deliberate scoped change.
