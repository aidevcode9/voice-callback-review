# Voice Callback Review workflow profile

Stage: owner-approved golden set v1.0 is frozen. No application exists.

## Source of truth

The [brief](../intake/PROJECT_BRIEF.md) owns open decisions, the [PRD](../docs/PRD.md) owns proposed behavior, and the [source register](../intake/README.md) distinguishes user instructions from recommendations. Follow the shared [build process](../docs/HOW_WE_BUILD.md).

## Current skill choices

- Project orchestration: bundled [project-workflow](../.agents/skills/project-workflow/SKILL.md).
- Discovery support: installed `workflow-skill-manager`, using this project-specific profile.
- Lead for intake: bundled `project-intake`.
- Documentation: pstack `technical-writing` and `unslop`, read from the current installed environment.
- Review and handoff: `code-review-workflow`, `verification-before-completion`, and `branch-finish` when relevant.
- Later substantial implementation: compare `planning-workflows` with pstack Feature for the selected task. No implementation workflow is selected yet.
- Later hard runtime bugs: consider pstack Bug fix when its required tools are available.

The intake and project-workflow skills are bundled. For every substantial task, inspect relevant pstack and house candidates, then record the choice and reason. See [workflow selection](../docs/WORKFLOW_SELECTION.md) for this stage's actual decisions. Other names describe this session's available skills, not portable installation guarantees. There is no application-specific preflight runner.

## Validation at this stage

For documentation changes, inspect relative links, source claims, and diagram consistency with the written behavior, then run `git diff --check` for tracked edits and `git diff --cached --check` before commit. Structural validation of the bundled skill uses the installed skill-creator validator when available.

Application, model-quality, audio-quality, UI, and integration checks cannot run before implementation. Define actual commands and passing conditions in the selected feature's plan before coding. Do not treat missing commands as passed checks.

## Data validation commands

- `python scripts/freeze_gold.py --check` verifies the frozen release, source/policy approval bindings, hashes, and exact exports.

- `python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl` validates structure and reports counts.
- `python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check` detects packet drift.
- `python -m unittest discover -s tests -v` exercises CLI behavior and the actual starter artifacts.

Run these for candidate data or tool changes. They do not validate semantic label correctness or human approval.

## Project invariants

- Candidate labels are not gold until reviewed under a stated rubric.
- Held-out expected labels do not enter classifier inputs.
- Transcription failures do not become no-callback decisions.
- Model output, reviewer decision, and the expected gold label stay distinguishable.
- A displayed evidence excerpt refers to the transcript version used.
- Demo data is proposed to be fictional. No real customer source data has been supplied.

Product acceptance and model quality remain open. Preparing this PRD does not claim that an application is implemented or fit for operational use.
