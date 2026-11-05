# F-003: Human review and gold-set freeze

Lifecycle status: backlog.
Owner and acceptance owner: the user for human labels; agent for preparation and structural checks.
Dependencies: completed F-001 policy and F-002 candidate preparation.
Product requirements: PRD-R006 and PRD-R007.

## Outcome

Review the 40 pending fictional cases against callback policy v1.0, resolve disagreements, and freeze a versioned gold release. The agent QA pass does not satisfy human label approval.

Start with [the candidate review packet](../../../data/candidates/v0.1/REVIEW.md). The [label guide](../../../docs/LABEL_GUIDE.md) defines the process. Dataset size, language, and split defaults remain revisable before freezing.

## Acceptance criteria

| ID | Observable criterion |
| --- | --- |
| F-003-AC01 | Each included case has an identified human reviewer, accepted label, rationale, and supporting evidence. Pending and rejected cases remain outside gold. |
| F-003-AC02 | Any disputed cases are resolved against the transcript and policy, with corrections recorded separately from original proposals. |
| F-003-AC03 | A gold manifest records policy and dataset versions, provenance, reviewed case IDs, and the frozen grouped split. |
| F-003-AC04 | Expected labels and reviewer notes remain outside the future classifier input contract. |

## Current state

All 40 cases are pending. No human label approvals, gold release, or model results exist. Next action: the owner reviews a batch of transcripts and confirms or corrects the proposed labels. Do not infer case approval from acceptance of the general policy.

Any export or model integration needed after review gets its own concrete implementation steps before code is written.
