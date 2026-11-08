# Project brief

Project: Voice Callback Review.
Intake status: draft, sufficient for product discussion.
Project and acceptance owner: the user.
Last reviewed: 2026-11-06.

## Problem and users

The user wants hands-on familiarity with voice applications for an interview conversation and wants to exercise a repeatable repository-based development workflow. The proposed product helps a service reviewer decide which callers need follow-up. Source: SRC-001.

Primary prototype user: the project owner demonstrating and evaluating the workflow. A law-firm service reviewer is the proposed end-user persona, not a validated customer.

## Scope and delivery

- Confirmed callback policy v1.0: unresolved issues, outstanding explicit requests, and promises require a callback; clear resolution with no separate obligation and non-actionable calls do not; uncertain cases need review. Sources: SRC-009 and SRC-010.
- Confirmed process: configure the project-workflow orchestrator during intake, before implementation; compare relevant pstack and house skills for substantive tasks. Sources: SRC-007 and SRC-008.
- Confirmed documentation preference: user-flow and architecture diagrams, with supporting diagrams where useful. Source: SRC-005.
- Confirmed: a separate local repository, a draft PRD, text inputs, and text-based callback evaluation. SRC-024 supersedes SRC-004's audio delivery scope.
- Confirmed: local open-model setup and explicit classifier choice. SRC-018 selects qwen3.5:4b-q4_K_M and authorizes explicit provisioning and development-only inference.
- Confirmed build scope: F-004 owns local runtime and text classification/evaluation. F-006 owns the implemented frontend/API. SRC-024 moves transcription and paired audio to the future roadmap; SRC-016 and SRC-020 retain their historical record.
- Current demo: fictional text, a three-way callback recommendation, evidence, a review dashboard, and an independently labeled evaluation set.
- Proposed data: fictional English-language service call transcripts. No actual customer corpus has been supplied.
- Excluded from the proposed demo: live telephony, autonomous callbacks, CRM integration, legal advice, case qualification, and production operation.
- Success: a clear demo and an honest explanation of requirements, examples, evaluation, mistakes, and iteration.
- Delivery date and deployment target: not specified.

## Stack and system context

F-004 provides local diagnostics and a text-classification CLI. Ollama 0.40.15 serves the selected qwen3.5:4b-q4_K_M model. [Local model options](../docs/LOCAL_MODEL_OPTIONS.md) records the comparison, selection, and hardware limits. Each classification saves an exclusive local run record. Batch 3 implements evaluation/scoring/freeze commands with a preserved text-v1 baseline; fresh text-v2 verification/freeze remain pending. F-006 implements the selected A text Review desk, FastAPI/SQLite and Nginx. Controlled browser integration is verified. Optional Langfuse tracing is separately configured and can send data to the configured service.

The active feature documents own implementation and verification. D-004 quality targets and D-005 hosting remain owner decisions.

## Assumptions and proposals

| Item | Status | Basis | Consequence |
| --- | --- | --- | --- |
| Text transcript input; audio upload and transcription deferred | User-selected | SRC-024 supersedes the audio portion of SRC-004 | Current delivery and quality work concern text. |
| Browser dashboard | Proposal | SRC-001 suggested a simple dashboard | Keep the interface focused on review and evaluation. |
| Three outcomes and final-resolution boundary | User-accepted | SRC-009 and SRC-010 | Apply callback policy v1.0 to candidate examples. |
| Golden labels require human review | Proposal | Evaluation needs a reference independent of candidate predictions | Model-generated labels remain candidates until reviewed. |
| Fictional English-language data | Proposal | No real corpus or language requirement supplied | Keep the first experiment small and reproducible. |

## Decisions

| ID | Decision | Owner | What it blocks |
| --- | --- | --- | --- |
| D-001 | Resolved: callback policy v1.0 accepted, including the final-resolution boundary and outstanding-obligation exception. | User | No remaining policy blocker for candidate preparation. |
| D-002 | Resolved for v1.0: the owner approved all 40 labels as-is. The release freezes the prepared English-language set and grouped 20/20 assignments. | User approval; agent export | No remaining gold-preparation blocker; operational model quality is separate. |
| D-003 | The Python core, Ollama classifier, and Next.js/Nginx/FastAPI direction are implemented. SRC-018 selects qwen3.5:4b-q4_K_M. Audio model and runtime choices are deferred under SRC-024. | User with implementation recommendation | Current model-quality acceptance; future audio choices are separate. |
| D-004 | Minimum acceptable decision quality and review workload | User, informed by baseline results | A claim that the model is fit for a defined use. |
| D-005 | Local demo versus hosted sharing | User | Deployment work only. |

## Intake outcome

The PRD remains a draft for the wider product. F-001 completed the accepted callback policy, labeling guide, and proposed candidate plan. F-002 completed 40 synthetic candidates, a readable review packet, and offline checks. F-003 recorded owner approval of all 40 labels and froze gold v1.0. F-004 is active with text classification and evaluation implemented; a historical text-v1 baseline is preserved. Fresh text-v2 baseline/freeze and quality acceptance remain pending. Audio is deferred. No overall product-quality acceptance is claimed.

## Text workspace decision, SRC-020

The owner rejected Streamlit and approved Next.js with Nginx proxying /api to a thin FastAPI boundary over the Python core. F-006 owns frontend/API requirements and browser acceptance; F-004 keeps core text evaluation. SRC-024 supersedes SRC-020's audio sequence. Two rendered alternatives preceded visual selection. All prototypes use fictional simulations. The callback-text-v2 baseline/freeze, numeric quality targets, product acceptance and hosting remain open. Historical v1 baseline evidence is preserved. No held-out cases or answers belong in the iterative UI.

SRC-021 resolves the visual choice: A Review desk is selected and implementation is authorized. Visual acceptance does not accept unimplemented behavior, model quality or deployment.
