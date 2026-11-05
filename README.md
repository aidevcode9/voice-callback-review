# Voice Callback Review

A learning prototype for reviewing recorded service calls and identifying which callers need a callback. The intended interface is a small browser dashboard.

Project stage: callback policy accepted and candidate preparation completed. Forty fictional cases are ready for human review. No application or model evaluation has been implemented.

## Start here

- [Product requirements](docs/PRD.md) describe the proposed behavior and open decisions.
- [Project brief](intake/PROJECT_BRIEF.md) separates user instructions from recommendations.
- [Source register](intake/README.md) records the context supplied so far.
- [User flow](docs/USER_FLOW.md), [architecture](docs/ARCHITECTURE.md), and [evaluation](docs/EVALUATION.md) include proposed diagrams.
- [Workflow selection](docs/WORKFLOW_SELECTION.md) records which skills are used and what has actually run.
- [Demo story](docs/DEMO_STORY.md) outlines how to explain the product and development workflow.
- [Documentation map](docs/README.md) links the remaining project documents.

The user selected audio upload and text transcript input for the demo, with callback decisions evaluated on text first. Callback policy v1.0 is accepted; dataset preparation and application choices are tracked separately.

## Planned flow

Upload a recording or supply a text transcript. Review the transcript, callback recommendation, reason, and supporting excerpt. Compare recommendations against independently reviewed examples.

## Continue work

[F-001: callback rubric](features/completed/F-001-callback-rubric/FEATURE.md) is completed: the accepted policy, labeling procedure, and candidate preparation plan are recorded. [F-002: candidate preparation](features/completed/F-002-candidate-set/01_REQUIREMENTS.md) is completed. Next is [F-003: human review and gold freeze](features/backlog/F-003-human-gold-review/FEATURE.md).

Use [project-workflow](.agents/skills/project-workflow/SKILL.md) as the project's orchestration entrypoint. It was configured during intake, before implementation, and compares relevant pstack and house skills for substantive tasks.

The [workflow profile](.codex/workflow-profile.md) records the current skill choices and validation limits. The stack, model provider, application commands, and hosting remain undecided.

This repository was generated from the project-template starter at commit `bac0ba6f1a4e46fda0c09fdcacaef8e01243a61d`. During intake it adopted the version 0.2 orchestration and diagram update from `52a045957eac7eaddf9ba533b628d88e893cc933`. It has its own local Git history. The shared [build process](docs/HOW_WE_BUILD.md) governs later feature work.

## Review the starter cases

Open [the 40-case review packet](data/candidates/v0.1/REVIEW.md). All labels are proposals and remain pending; the agent QA pass did not approve them as gold.

```powershell
python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl
python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check
python -m unittest discover -s tests -v
```

These offline checks use Python 3.10 or later and no API credentials. They validate data preparation, not model quality.
