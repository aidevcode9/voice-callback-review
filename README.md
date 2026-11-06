# Voice Callback Review

A learning prototype for reviewing recorded service calls and identifying which callers need a callback. The intended interface is a small browser dashboard.

Project stage: 40 owner-approved fictional cases are frozen as golden set v1.0. F-004 is active. Batches 1 and 2 implement diagnostics, an explicit model registry, and local text classification with validated evidence and run provenance. Batch 3 implements development evaluation, offline scoring, and configuration freezing; live baseline evidence is pending. Audio and dashboard remain planned.

## Start here

- [Product requirements](docs/PRD.md) describe the proposed behavior and open decisions.
- [Project brief](intake/PROJECT_BRIEF.md) separates user instructions from recommendations.
- [Source register](intake/README.md) records the context supplied so far.
- [User flow](docs/USER_FLOW.md), [architecture](docs/ARCHITECTURE.md), and [evaluation](docs/EVALUATION.md) include proposed diagrams.
- [Quality checks](docs/QUALITY_CHECKS.md) defines the shared local/CI gates, snapshot preflight, and Actions cost limits.
- [Local setup](docs/LOCAL_SETUP.md) creates the environment, explicitly provisions the selected model, and runs diagnostics/classification.
- [Local model options](docs/LOCAL_MODEL_OPTIONS.md) records laptop fit, the selected classifier, and its alternatives.
- [Workflow selection](docs/WORKFLOW_SELECTION.md) records which skills are used and what has actually run.
- [Demo story](docs/DEMO_STORY.md) outlines how to explain the product and development workflow.
- [Documentation map](docs/README.md) links the remaining project documents.

The user selected audio upload and text transcript input for the demo, with callback decisions evaluated on text first. Callback policy v1.0 is accepted; dataset preparation and application choices are tracked separately.

## Planned flow

Upload a recording or supply a text transcript. Review the transcript, callback recommendation, reason, and supporting excerpt. Compare recommendations against independently reviewed examples.

## Continue work

[F-001: callback rubric](features/completed/F-001-callback-rubric/FEATURE.md) is completed: the accepted policy, labeling procedure, and candidate preparation plan are recorded. [F-002: candidate preparation](features/completed/F-002-candidate-set/01_REQUIREMENTS.md) is completed. [F-003: human review and gold freeze](features/completed/F-003-human-gold-review/FEATURE.md) is completed. The active build is [F-004: local model pipeline](features/active/F-004-local-model-pipeline/01_REQUIREMENTS.md), with separate [technical specification](features/active/F-004-local-model-pipeline/02_TECHNICAL_SPEC.md) and [implementation plan](features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md). Batch 2 implements the owner-selected qwen3.5:4b-q4_K_M classifier. Development checks are recorded in its plan; quality targets remain open.

Use [project-workflow](.agents/skills/project-workflow/SKILL.md) as the project's orchestration entrypoint. It was configured during intake, before implementation, and compares relevant pstack and house skills for substantive tasks.

The [workflow profile](.codex/workflow-profile.md) records the current skill choices and validation limits. Ollama responds locally. Doctor and models commands are available through the [setup guide](docs/LOCAL_SETUP.md). F-004 implements text inference and evaluation commands; transcription and the dashboard remain proposed. Hosting remains undecided.

This repository was generated from the project-template starter at commit `bac0ba6f1a4e46fda0c09fdcacaef8e01243a61d`. During intake it adopted the version 0.2 orchestration and diagram update from `52a045957eac7eaddf9ba533b628d88e893cc933`. It has its own local Git history. The shared [build process](docs/HOW_WE_BUILD.md) governs later feature work.

## Golden set v1.0

Open [the frozen golden set](data/gold/v1.0/README.md) and its [manifest](data/gold/v1.0/manifest.json). The owner approved all 40 labels as-is under [REVIEW-001](data/reviews/v1.0.json). The original candidate packet remains an unchanged historical snapshot; its pending fields describe the state before the separate approval.

```powershell
python scripts/freeze_gold.py --check
python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl
python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check
python -m unittest discover -s tests -v
```

These offline checks use Python 3.10 or later and no API credentials. They validate data preparation, not model quality.

## Engineering baseline

After installing the pinned development requirements, run `.venv\Scripts\python.exe scripts/check_project.py` for lint, format, types, behavior tests, data, docs, and a clean package smoke test. [Quality checks](docs/QUALITY_CHECKS.md) explains the staged/committed snapshot gates and GitHub Actions matrix. [F-005](features/completed/F-005-development-quality-baseline/01_REQUIREMENTS.md) establishes this baseline before F-004 batch 2; batch 2 adds the selected classifier.
