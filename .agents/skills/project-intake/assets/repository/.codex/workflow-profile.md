# Repository workflow profile

Configuration status: unresolved. Fill this profile during intake. Unresolved application commands are not passing checks.

## Project context

- Brief and stack decisions: [project brief](../intake/PROJECT_BRIEF.md).
- Product requirements: [PRD](../docs/PRD.md).
- Current system: [architecture](../docs/ARCHITECTURE.md).
- Source and test layout: TBD after stack selection.
- Runtime, deployment target, and important invariants: TBD.

## Skill routing

Choose based on the task and actual availability. Installed names below are candidates, not bundled dependencies.

Orchestration entrypoint: [project-workflow](../.agents/skills/project-workflow/SKILL.md). Intake configures this skill and profile after initial classification and scope, before implementation. For each substantial task, compare relevant pstack and house candidates before choosing.

| Situation | Lead workflow candidate | Add only when relevant |
| --- | --- | --- |
| New project or process adoption | Bundled `project-intake` | Existing source-specific document tools |
| Substantial feature | `planning-workflows`, or pstack Feature for deeper orchestration | Relevant implementation specialists |
| Bounded defect | `systematic-debugging` | Focused regression verification |
| Hard runtime or cross-system defect | pstack Bug fix | Its required investigation and surface tools |
| Significant architecture decision | pstack `architect`, if available | Independent alternatives and design evidence |
| Review and completion | `code-review-workflow`, `verification-before-completion` | Risk-specific checks |
| Commit or PR requested | Project's handoff workflow | Configured preflight and `branch-finish` if available |

- Available skills and versions or source revisions: TBD.
- Missing dependencies and permitted adaptations: TBD.
- Execution workflow for the current task: TBD after inspecting project and relevant pstack and house skills.
- For each substantial task, record the selected workflow and why in its feature plan.

If these candidates are absent, use the documented build process directly, state the missing capability, and keep all applicable verification requirements. Do not install or copy personal workflows automatically.

## Validation by changed surface

Replace TBD rows with exact commands, expected results, and evidence locations. Mark irrelevant surfaces as not applicable with a reason.

| Changed surface | Exact command or real flow | Passing result | When required |
| --- | --- | --- | --- |
| Documentation | TBD | Local links resolve and claims match the artifact | Relevant documentation changes |
| Core behavior | TBD | Defined acceptance and regression cases pass | Behavior changes |
| UI or CLI | TBD | Changed user flow produces its expected end state | Interaction changes |
| API and generated clients | TBD | Contract and consumer checks pass | Shared interface changes |
| Database | TBD | Migration and data integrity checks pass | Schema or persistence changes |
| Authorization and data boundaries | TBD | Allowed and denied cases behave correctly | Permission or scope changes |
| Async jobs and integrations | TBD | Success, failure, and retry behavior are observable | Relevant boundary changes |
| AI behavior | TBD | Representative cases and failure cases meet an explicit rubric | AI functionality changes |
| Performance | TBD | Relevant metric meets a justified budget | Performance-sensitive work |
| Release | TBD | Delivery and operational checks pass | Release work |

## Completion contract

- Required acceptance owner or delegated acceptance rule: TBD.
- Required evidence for the changed surface: TBD.
- Required integration or deployment work, if any: TBD.
- Publication and external-action scope: follow the user's actual authorization.
- If a required check is unavailable, report the missing check and its effect. Do not claim that gate passed.

## Required quality baseline

[quality-gates.json](../quality-gates.json) records the language, lint, formatter, type-check, behavior-test commands, shared local command, and CI file. Run `python scripts/check_quality_baseline.py` to validate that record. Documentation-only intake may leave tools unresolved until language selection; choosing a language or adding first-party code makes the record mandatory. Missing gates cannot silently count as passing.

For Python, use Ruff lint/format checks and Pyright type checking by default, with focused behavior tests. Other languages choose equivalent tools. Configure exact versions in an isolated development environment and record exceptions explicitly. Keep generated/vendor code and immutable data outside automatic formatting. Use the same check command in local work and CI, and test the declared minimum runtime plus the development platform.

Before handoff, run the configured checks against the staged index or committed tree, not unrelated dirty files. CI must have bounded jobs, read-only default permissions, and explicit cost/credential expectations. Report unavailable hosted runs and branch protection separately from local validation.
