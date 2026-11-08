# Voice Callback Review: product requirements

Status: living product requirements; text review workspace implemented, text quality acceptance pending, and audio deferred to the roadmap.
Product and acceptance owner: the user.
Sources: SRC-001, SRC-004, SRC-009, SRC-010, SRC-011, SRC-012 through SRC-019, and SRC-020 through SRC-022 in the [source register](../intake/README.md).
Last updated: 2026-11-07.
Acceptance record: input modes and callback policy v1.0 accepted. SRC-021 selects A Review desk. Next.js, loopback Nginx and a thin FastAPI API are implemented in F-006. Functional verification, owner feedback, quality thresholds, merge and hosting remain distinguishable.

## Purpose

Build a small post-call review application that recommends whether a service representative should call someone back. Use it to learn about voice application design and demonstrate a repository-based development process.

The interview context motivates a fictional law-firm service example. No company-specific operating policy has been supplied.

## Users and outcome

A reviewer can inspect a call, understand the callback recommendation, see the evidence behind it, and correct a mistake. The project owner can demonstrate how the system was specified and evaluated.

The core question is operational: does this conversation leave a callback action for a service representative? It does not assess legal merit or give legal advice.

## Confirmed input choice

The current demo accepts existing text transcripts and fictional development cases. SRC-024 supersedes SRC-004's audio delivery choice: audio upload and transcription are [future enhancements](ROADMAP.md).

## First-demo build scope

Local inference and explicit classifier selection are part of the build. SRC-018 selects qwen3.5:4b-q4_K_M for callback classification. The scope is specified in [F-004 requirements](../features/active/F-004-local-model-pipeline/01_REQUIREMENTS.md).

1. Supply a text transcript or load a fictional development case.
2. Retain the original transcript and identify any reviewer correction used for a new decision.
3. Recommend one of three outcomes and provide a short reason plus a supporting excerpt.
4. Display fictional development cases and preserved recommendations in the review workspace.
5. Compare model recommendations against a versioned golden set and inspect errors.

The initial text interface needs compact case navigation, useful outcome/review filters, an editable versioned transcript with evidence highlights, a separate human decision, and inspectable run history. Formal evaluation remains a separate CLI flow; held-out inputs and answers do not enter the iterative workspace. A numeric confidence percentage is not required. The first design should favor evidence the reviewer can inspect.

The [user flow](USER_FLOW.md), [architecture](ARCHITECTURE.md), and [evaluation flow](EVALUATION.md) show how these responsibilities connect.

## Accepted callback rubric

The user accepted [callback policy v1.0](CALLBACK_POLICY.md), including all proposed outcomes and the final-resolution boundary.

| Outcome | Accepted condition |
| --- | --- |
| callback_required | The issue remains unresolved, the caller has an outstanding callback request, or the representative has an outstanding callback promise. |
| no_callback | The issue is resolved with no outstanding follow-up, including one resolved later in the same call; or the call is clearly non-actionable spam or a wrong number. |
| needs_review | Incomplete, contradictory, or unintelligible conversation leaves resolution or follow-up unclear. |

A separate outstanding callback request or promise still requires a callback after the issue is resolved. Missing contact details do not erase an obligation. A recommendation does not establish that a callback occurred. Urgency scoring and service-level deadlines remain outside the first rubric.

## Product requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| PRD-R001 | Accept text transcripts. Audio upload is deferred to the roadmap. | Text produces an inspectable case; invalid input displays a useful error. |
| PRD-R002 | Preserve original and corrected transcript versions. Audio failure behavior is deferred. | The version used for each callback decision remains identifiable. |
| PRD-R003 | Apply the agreed callback rubric with an explicit needs-review option. | Representative labeled examples cover all outcomes, contradictory requests, and incomplete calls. |
| PRD-R004 | Show the reason and supporting transcript excerpt. | The excerpt exists in the transcript version used for the decision; unsupported claims are visible as failures. |
| PRD-R005 | Let a person inspect and correct a recommendation. | The dashboard distinguishes the original model output from the reviewer decision. It does not automatically relabel gold data. |
| PRD-R006 | Maintain an independently reviewed golden set. | Each accepted case has a stable ID, transcript, expected outcome, rationale, provenance, reviewer, and dataset version. |
| PRD-R007 | Evaluate a frozen system against held-out cases without label leakage. | A reproducible run identifies dataset, prompt, model, and input versions and reports counts and errors. |
| PRD-R008 | Make the development and demo process explainable. | The owner can walk through intake, requirements, a feature plan, golden labels, observed errors, and an iteration without claiming unrun results. |
| PRD-R009 | Select a callback classifier explicitly. Independent transcription selection is deferred. | The selector reports unavailable models. Each run records runtime, model identity, settings, and transcript version. There is no silent download or cloud fallback. |
| PRD-R010 | Make the local inference environment reproducible on the owner's laptop. | Runtime diagnostics distinguish installation, server availability, installed compatible models, and successful inference. Setup uses explicit local model provisioning without paid API credentials; failures and GPU limits are visible. |
| PRD-R011 | Require explicit inference submissions and preserve versioned history. | Selector, filter, navigation and editing changes invoke no inference. Saved edits create a new version, and earlier outputs retain original input/model provenance after reload. Owned by F-006. |
| PRD-R012 | Provide one-origin local text review. | Next.js/Nginx/FastAPI boundaries enforce one active job, bounded requests, visible failures, and separate reviewer records. F-006 owns browser/API acceptance. |

The user wants local open-model development and selected qwen3.5:4b-q4_K_M under SRC-018. See [local model options](LOCAL_MODEL_OPTIONS.md) for observed hardware, recommendations, and remaining setup. Provider choices are not inferred from those recommendations.

## Build sequence

[F-004](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) owns the core and formal text evaluation. [F-006](../features/completed/F-006-text-review-workspace/03_IMPLEMENTATION_PLAN.md) owns the frontend/API, text review flow and browser acceptance.

1. Add model-independent contracts, Ollama diagnostics, and compatible-model discovery.
2. Select a classifier and implement policy-grounded text decisions with validated evidence.
3. Evaluate on development text, then freeze a configuration before held-out evaluation.
4. Review two rendered text-workspace directions and choose one before production implementation (F-006).
5. Implement the text API and Next.js workspace behind local Nginx; verify explicit submissions, transcript versions, earlier results and separate human review (F-006).
6. Harden the text workflow and prepare the leadership demonstration; scope future work separately.

The classifier is already selected and its core is merged. A fresh development quality run, numeric quality targets and hosted sharing remain separate open decisions.

## Golden set and evaluation

Start with a proposed small candidate collection of roughly 30 to 50 fictional transcripts. Include clear positives, clear negatives, ambiguous cases, truncated conversations, explicit callback promises, already-resolved requests, and wording variations. The owner approved all 40 English-language candidates as-is (SRC-011). Golden set v1.0 freezes the prepared grouped 20/20 splits with separate model inputs and expected answers. See the [candidate-set plan](CANDIDATE_SET_PLAN.md).

A person reviews candidate labels using the rubric before the collection is called gold. Candidate model outputs cannot define their own expected answers. Keep development examples separate from held-out evaluation cases, and keep related conversations or paraphrases in the same split.

Report a three-outcome confusion matrix, strict callback recall, callback precision, needs-review rate, and concrete mistakes. Strict recall counts a needs-review output as not automatically detecting a required callback. Also report unsafe misses where a gold callback-required case is predicted no callback. Show small-sample counts beside percentages.

Do not silently discard needs-review cases or change expected labels to improve a run. Changes to labels create a new dataset version with a recorded reason. The initial classifier is selected under SRC-018. Later model changes and numeric quality thresholds require development evidence and the acceptance owner's decision.

The historical callback-text-v1 development baseline matched 20/20 fictional labels once. A fresh callback-text-v2 baseline/freeze and quality acceptance remain pending. A future audio extension would need paired recordings and reviewed reference transcripts; see the [roadmap](ROADMAP.md).

## Exclusions

Live phone handling, speaking agents, automatic dialing, CRM writes, legal guidance, case qualification, production authentication, and production multi-firm deployment are outside the proposed first demo. No real customer recordings are needed for the learning prototype.

## Proposed acceptance flow

A reviewer supplies text or a fictional development input, explicitly submits a selected model, inspects its recommendation and exact quote, and records a separate human decision. Expected answers are not exposed in this iterative flow. Formal evaluation remains separate and produces an inspectable report, including failures and review cases.

Functional implementation and decision quality are separate acceptance areas. No product-quality threshold or acceptance result is approved by this draft.

Open decisions and owners are tracked in the [project brief](../intake/PROJECT_BRIEF.md). F-001 accepted the rubric, F-002 prepared candidates, and F-003 froze approved gold. F-004 implements diagnostics, classification, and evaluation with offline evidence; the fresh callback-text-v2 baseline and candidate freeze remain pending. F-006 completes the text Review desk, API/SQLite, and local Nginx proxy. D-004 quality targets are open.

## Text workspace delivery, 2026-11-07

F-006 delivers pasted and explicitly loaded fictional text, available-model selection, explicit idempotent classification, immutable transcript/run history, exact evidence highlights, separate append-only human decisions, filters and provenance. The [feature requirements](../features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) are the feature PRD; its plan maps acceptance criteria to evidence. The Next.js/Nginx/FastAPI flow is exercised with controlled HTTP responses, not live model-quality measurement. Fresh text-v2 development evaluation, numeric quality targets, held-out execution and hosting remain open. Audio is deferred.
