# Voice Callback Review

A learning prototype for reviewing recorded service calls and identifying which callers need a callback. The implemented interface is a local browser Review desk.

Project stage: 40 owner-approved fictional cases are frozen as golden set v1.0. F-004 is complete for the text pipeline after owner testing and QA acceptance (SRC-026). F-006 delivers the Next.js Review desk with FastAPI/SQLite and a loopback Nginx proxy. [F-011](features/completed/F-011-evaluation-workflow/01_REQUIREMENTS.md), merged through [PR #7](https://github.com/aidevcode9/voice-callback-review/pull/7), provides one evaluation command, readable browser reports, and saved baseline comparison. The current-source callback-text-v2 development run matched 20/20 labels; see [evaluation evidence](docs/EVALUATION.md). Candidate freeze, real held-out evaluation, numeric production-quality targets, hosting, and [audio/transcription](docs/ROADMAP.md) remain separate follow-up work.

## Start here

- [Technical roadmap](docs/ROADMAP.md) defines future production hardening, login/access, observability, AI security, deployment/CI/CD, and audio work for the technical team.
- [Product requirements](docs/PRD.md) describe the proposed behavior and open decisions.
- [Classifier prompts](docs/CLASSIFIER_PROMPTS.md) identifies the versioned instruction file and how changes are verified.
- [Project brief](intake/PROJECT_BRIEF.md) separates user instructions from recommendations.
- [Source register](intake/README.md) records the context supplied so far.
- [User flow](docs/USER_FLOW.md), [architecture](docs/ARCHITECTURE.md), and [evaluation](docs/EVALUATION.md) include proposed diagrams.
- [Quality checks](docs/QUALITY_CHECKS.md) defines the shared local/CI gates, snapshot preflight, and Actions cost limits.
- [Evaluation workflow](features/completed/F-011-evaluation-workflow/01_REQUIREMENTS.md) makes development runs, saved reports and baseline comparison one packaged workflow.
- [Langfuse tracing](docs/LANGFUSE.md) describes optional operational traces and the TCO worksheet.
- [Local setup](docs/LOCAL_SETUP.md) creates the environment, explicitly provisions the selected model, and runs diagnostics/classification.
- [Local model options](docs/LOCAL_MODEL_OPTIONS.md) records laptop fit, the selected classifier, and its alternatives.
- [Workflow selection](docs/WORKFLOW_SELECTION.md) records which skills are used and what has actually run.
- [Demo story](docs/DEMO_STORY.md) outlines how to explain the product and development workflow.
- [Documentation map](docs/README.md) links the remaining project documents.

The current demo uses text transcripts. SRC-024 defers the earlier audio upload choice to the roadmap. Callback policy v1.0 is accepted; dataset preparation and application choices are tracked separately.

## Current text flow

Paste text or explicitly load a fictional development case, select a classifier, submit, inspect highlighted evidence and policy rules, then record a separate human decision. Preserve transcript versions and earlier runs. Held-out cases and answers stay out of the iterative workspace.

## Continue work

[F-001: callback rubric](features/completed/F-001-callback-rubric/FEATURE.md), [F-002: candidate preparation](features/completed/F-002-candidate-set/01_REQUIREMENTS.md), and [F-003: human review and gold freeze](features/completed/F-003-human-gold-review/FEATURE.md) are complete. [F-004: local model pipeline](features/completed/F-004-local-model-pipeline/01_REQUIREMENTS.md) is complete for its accepted text scope; its [plan](features/completed/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md#owner-qa-closeout-src-026-2026-11-08) records QA acceptance, current development evidence, and transferred work. [F-006](features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) owns the implemented Review desk; [F-011](features/completed/F-011-evaluation-workflow/01_REQUIREMENTS.md) owns the coherent evaluation workflow. Follow-up quality and audio work is recorded in the [roadmap](docs/ROADMAP.md).

Use [project-workflow](.agents/skills/project-workflow/SKILL.md) as the project's orchestration entrypoint. It was configured during intake, before implementation, and compares relevant pstack and house skills for substantive tasks.

The [workflow profile](.codex/workflow-profile.md) records the current skill choices and validation limits. Ollama responds locally. Doctor and models commands are available through the [setup guide](docs/LOCAL_SETUP.md). F-004 implements text inference and evaluation commands; F-006 adds the text review desk. Transcription remains proposed. Hosting remains undecided.

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

## Text review workspace

[F-006](features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) delivers selected A Review desk, FastAPI/SQLite persistence, and Nginx routing `/api` to the Python core. Use the [setup guide](docs/LOCAL_SETUP.md#run-the-review-desk) to start the app. [Browser evidence](docs/evidence/F-006/README.md) records controlled functional verification using an Ollama HTTP fixture. The [two visual directions](prototypes/text-review/index.html) remain historical simulations. The [engineering workflow map](docs/vc-review-map.html) includes the separate evaluation path and current acceptance status.

The owner selected A Review desk under SRC-021 and accepted F-004 text testing and QA under SRC-026. Development results measure the fictional development cases. Numeric production-quality targets and deployment remain open; audio is deferred.
