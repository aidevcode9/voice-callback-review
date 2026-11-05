# F-001: Define the callback rubric

Owner and acceptance owner: the user.
Product requirements: PRD-R003 and PRD-R006.
Lifecycle status: completed.
Dependencies: D-001 and D-002 in the project brief.
Orchestrator: project-workflow.
Execution workflow: bounded product specification using project-intake and pstack writing skills.
Candidate clarification skills inspected: pstack in-your-own-words and sharpen; neither replaces the requested product documents.

## Requirements

Agree on the meaning of callback required, no callback required, and needs review before creating gold labels. Define how a human reviewer handles incomplete conversations, promised callbacks, contradictory statements, and resolved requests.

This is a small documentation feature. It does not implement a model, create a full dataset, transcribe audio, or build the dashboard.

| Acceptance ID | Observable criterion |
| --- | --- |
| F-001-AC01 | The decision owner records the accepted label definitions and boundaries with examples. |
| F-001-AC02 | The labeling procedure distinguishes candidate labels from reviewed gold, including conflicts and later corrections. |
| F-001-AC03 | A proposed candidate set plan names case categories, reviewer, dataset size, and development/evaluation split rules. |

## Technical approach

No application design is needed. Update the PRD if policy changes and add a label guide when the policy is agreed. Record examples as fictional. Use stable case IDs when actual examples are created.

## Implementation and verification

- [x] Record the user's unresolved-issue decision as UR-001 with policy example POLICY-001 (SRC-009).
- [x] Record acceptance of the full v1.0 rubric (SRC-010).
- [x] Write the label guide and reviewer procedure.
- [x] Prepare the proposed D-002 candidate-set plan required by F-001-AC03. Human review and final gold-freeze decisions remain open.
- [x] Review AC01-AC03 against the policy, label guide, and proposed candidate plan.

## Completion evidence

Completed 2026-11-05 as a documentation feature.

| Criterion | Evidence |
| --- | --- |
| F-001-AC01 | Callback policy v1.0 is accepted under SRC-009 and SRC-010 and includes boundary examples. |
| F-001-AC02 | docs/LABEL_GUIDE.md defines pending, reviewed, and gold states, disputes, and versioning. |
| F-001-AC03 | docs/CANDIDATE_SET_PLAN.md proposes 40 English-language cases, the user as reviewer, scenario categories, and grouped 20/20 splits. These defaults remain proposed until freeze. |

An independent policy review found an ambiguous uncertainty path in the decision diagram. The diagram was corrected and the reviewer confirmed resolution. Local document links resolve. No model or application check applies to this documentation feature.

Candidate preparation is F-002. Human label review, D-002's final gold-freeze choices, and model evaluation are not completed by closing F-001. No deployment is part of this feature.
