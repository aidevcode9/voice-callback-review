---
name: project-workflow
description: "Coordinate planning, implementation, debugging, review, and handoff in this repository using its project profile and available skills. Use for substantive project tasks."
---

# Voice Callback Review workflow

Use this as the project's orchestration entrypoint. Read the [README](../../../README.md), relevant [feature documents](../../../features/README.md), and [workflow profile](../../../.codex/workflow-profile.md). The profile owns project-specific commands and invariants.

## Select the task workflow

1. Classify the request and affected behavior. Check the current PRD, feature status, and open decisions. If intake is incomplete for the requested work, use the sibling [project-intake](../project-intake/SKILL.md) to resolve the relevant gaps.
2. Discover the skills actually available in this environment. For a substantial task, read the relevant pstack candidate and relevant house skill before choosing. Use the profile's candidates to narrow discovery. The installed `workflow-skill-manager` can assist when available.
3. Choose one execution workflow based on expected outcome, design uncertainty, affected risks, tool availability, and cost. Existing skills are candidates, not automatic winners. Record the selected workflow, alternatives considered, and reason in the feature plan or workflow-selection document.
4. Read the selected skill and follow its applicable steps. Add only supporting skills needed for the task. If a full pstack playbook is selected, follow it and report missing capabilities. If borrowing techniques, label the method as adapted. Do not claim a playbook ran because it was inspected.

| Task | Compare relevant candidates |
| --- | --- |
| Intake and product definition | `project-intake`, focused writing skills, and relevant pstack investigation or clarification skills |
| Substantial feature | House `planning-workflows` and pstack Feature, including its required design exploration |
| Bug | House `systematic-debugging` and pstack Bug fix; use runtime evidence and task scope to choose |
| Uncertain design | Relevant house design skills and pstack `architect` |
| Review | House `code-review-workflow` and relevant pstack `interrogate` or `blast-radius` |
| Demonstrating real app behavior | Project checks and relevant pstack `create-verification-skill` when available |

Availability and the actual instructions determine what can run. Do not install missing skills automatically. Use an appropriate available method and identify the missing capability.

## Carry out the project work

- Follow the selected execution workflow within the user's scope. Substantial features use requirements, technical specification, and implementation plan files; small changes use one document.
- Maintain user-flow and architecture diagrams where they clarify the product or design. Label proposals and update diagrams with meaningful changes.
- Keep the selected feature's plan current, including blockers, evidence, and the next action when pausing.
- Review the changed behavior and run the profile's applicable checks before completion claims. Use available review and verification skills, including `verification-before-completion`. Unavailable or inconclusive checks remain explicit.
- For a requested Git handoff, apply the available branch-finish method. Preserve existing authorization; the skill itself grants no additional publication or deployment scope.

Intake configures this orchestrator after initial project classification and scope, before implementation begins. Revisit routing when the stack, risks, or task change. The orchestrator chooses and coordinates skills; the profile supplies project facts and validation.
