# Feature lifecycle

A feature lives in one folder under `backlog/`, `active/`, or `completed/`. Use an unused stable ID such as `F-001-short-name`. The folder location is the lifecycle status. Record blockers and progress in the feature documents.

## Choose a document size

Use [_templates/small/FEATURE.md](_templates/small/FEATURE.md) for a bounded change with a clear design and limited coordination risk. It contains requirements, technical approach, implementation, and evidence.

Use the three files under [_templates/substantial/](_templates/substantial/) for work with multiple layers, uncertain design, migration risk, or enough scope to need independent requirements and design review:

- [Requirements](_templates/substantial/01_REQUIREMENTS.md) owns intended behavior, acceptance criteria, and exclusions.
- [Technical specification](_templates/substantial/02_TECHNICAL_SPEC.md) owns design, interfaces, data, and failure behavior.
- [Implementation plan](_templates/substantial/03_IMPLEMENTATION_PLAN.md) owns sequencing, progress, and verification evidence.

If small work grows, expand its document into the three files while preserving feature and acceptance IDs. Avoid maintaining both representations.

## Move a feature

1. Capture an idea in backlog. A requirements draft is enough.
2. Before substantial implementation, finish the relevant scope, design, and verifiable checkpoints.
3. Move selected, unblocked work to active. User authorization may already be present.
4. Keep progress and pause notes in the plan or small feature document.
5. Move the folder to completed only after the [completion process](../docs/HOW_WE_BUILD.md) and project profile conditions are met.
6. Update links to moved documents. Keep feature IDs stable.

Do not claim a feature is deployed merely because its folder is completed. Record delivery state explicitly. If deployment is part of its agreed scope, complete that work before closing the feature.
