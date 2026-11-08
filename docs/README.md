# Documentation map

| Document | Authority |
| --- | --- |
| [Project brief](../intake/PROJECT_BRIEF.md) | Intake synthesis, assumptions, constraints, and open decisions. |
| [Source register](../intake/README.md) | Provenance and locations of supplied source material. |
| [Callback policy](CALLBACK_POLICY.md) | Accepted v1.0 label rules and final-resolution precedence. |
| [Classifier prompts](CLASSIFIER_PROMPTS.md) | Packaged instruction assets, prompt/version/hash ownership and change verification. |
| [Label guide](LABEL_GUIDE.md) | Human review, candidate/gold distinction, disputes, and versioning. |
| [Candidate-set plan](CANDIDATE_SET_PLAN.md) | Proposed size, reviewer, language, grouping, and split defaults. |
| [PRD](PRD.md) | Working product intent, scope, users, and product requirements. |
| [Demo story](DEMO_STORY.md) | Planned walkthrough of the product and development process. |
| [User flow](USER_FLOW.md) | Proposed reviewer journey and processing-error paths. |
| [Golden set](../data/gold/v1.0/README.md) | Current frozen, owner-approved labels and isolated input/answer artifacts. |
| [Gold manifest](../data/gold/v1.0/manifest.json) | Versions, frozen splits, provenance, and file hashes. |
| [Human approval](../data/reviews/v1.0.json) | Explicit owner acceptance bound to candidate and policy snapshots. |
| [Candidate review packet](../data/candidates/v0.1/REVIEW.md) | Historical proposed-label snapshot before the separate human approval. |
| [Candidate data](../data/candidates/v0.1/README.md) | Data format, provenance, reproduction commands, and limitations. |
| [Evaluation](EVALUATION.md) | Implemented text evaluation, artifact integrity, metrics, freeze controls, and proposed audio comparison. |
| [Workflow selection](WORKFLOW_SELECTION.md) | Selected skills, orchestration role, and actual process stage. |
| [Local model build plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) | Sequenced implementation batches, model-choice dependencies, and acceptance evidence. |
| [Quality checks](QUALITY_CHECKS.md) | Shared static, behavior, data, documentation, package, and snapshot gates; CI costs and limits. |
| [Langfuse tracing](LANGFUSE.md) | Optional metadata-only tracing, setup, and privacy boundaries. |
| [Local setup](LOCAL_SETUP.md) | Reproducible project environment, runtime diagnostics, registry states, and offline checks. |
| [Local model options](LOCAL_MODEL_OPTIONS.md) | Observed laptop/runtime, classifier comparison and selection, and selectable-stage requirements. |
| [Architecture](ARCHITECTURE.md) | Current system structure and ownership. Proposed designs stay labeled. |
| [How we build](HOW_WE_BUILD.md) | Shared intake, implementation, and completion process. |
| [Feature lifecycle](../features/README.md) | Status transitions, document sizes, and feature templates. |
| [Workflow profile](../.codex/workflow-profile.md) | Project-specific skill routing and validation commands. |
| [Decision records](decisions/README.md) | Significant decisions and their rationale. |

The PRD records intended behavior. Code and runtime observations establish current behavior. A discrepancy must be reconciled, not hidden by editing acceptance evidence. The user's current instructions govern the requested work; source commitments that conflict with them need an explicit decision.

Keep permanent documentation current. Completed feature documents preserve what was delivered at that time. Link to existing facts rather than repeating them across files.

## Text workspace design

- [F-006 requirements](../features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md), [API/design specification](../features/completed/F-006-text-review-workspace/02_TECHNICAL_SPEC.md), and [plan/evidence](../features/completed/F-006-text-review-workspace/03_IMPLEMENTATION_PLAN.md) own the proposed text frontend/API.
- [Interactive directions](../prototypes/text-review/index.html) and [prototype verification notes](../prototypes/text-review/README.md) show the design exploration.
- [Product context](../PRODUCT.md) captures durable design constraints; [visual design record](../DESIGN.md) records selected A Review desk and preserves B Casebook as alternative evidence.
- [Text review surface brief](TEXT_REVIEW_DESIGN_BRIEF.md) records the proposed Operate directions and design workflow adaptation.

## Implemented Review desk

- [Startup and verification](LOCAL_SETUP.md#run-the-review-desk) runs the built Next.js/Nginx/FastAPI stack locally.
- [Production surface contract](REVIEW_DESK_SURFACE.md) carries selected A into the implementation.
- [Browser evidence](evidence/F-006/README.md) records functional scope and desktop/narrow captures.
- [Generated OpenAPI](api/openapi.json) and web/lib/api.generated.ts share strict Python response contracts with the runtime-validated client.
