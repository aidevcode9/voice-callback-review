# {{PROJECT_NAME}}

Project stage: intake. Product scope, stack, and application commands remain unresolved until intake is completed.

Read the [documentation map](docs/README.md) for product, architecture, and process documents. Start a new project with [intake](intake/README.md). Find feature lifecycle rules in [features/README.md](features/README.md).

## Run the project

No application runtime has been selected. During intake, replace this paragraph with prerequisites, setup, local run commands, and the main user flow. Keep exact validation commands in the [workflow profile](.codex/workflow-profile.md).

## Continue work

Read the [project brief](intake/PROJECT_BRIEF.md), the [PRD](docs/PRD.md), and the relevant feature under `features/active/`. Start new ideas under `features/backlog/`. Folder location records feature lifecycle status.

The [build process](docs/HOW_WE_BUILD.md) explains how we select skills, implement features, and verify completion.

Use [project-workflow](.agents/skills/project-workflow/SKILL.md) to coordinate ongoing tasks. Intake configures it and the repository profile before implementation. Record choices in [workflow selection](docs/WORKFLOW_SELECTION.md). Include [user-flow diagrams](docs/USER_FLOW.md) and architecture diagrams as the design becomes clear.

## Engineering baseline

Before source implementation, configure [quality-gates.json](quality-gates.json) for linting, formatting, type checking, behavior tests, the shared local check command, and CI. Run `python scripts/check_quality_baseline.py` to check the record. See the [workflow profile](.codex/workflow-profile.md) for stack-specific choices. Unknown tools may be deferred only during documentation-only intake before language selection.
