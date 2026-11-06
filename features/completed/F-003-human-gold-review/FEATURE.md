# F-003: Human review and gold-set freeze

Lifecycle status: completed.
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

## Technical approach and implementation plan

Orchestrator: project-workflow. Execution: house planning-workflows, supported by pstack writing skills. Pstack Feature was inspected; the export uses a fixed data contract and does not need competing application designs. A focused independent review will inspect approval provenance, immutability, and input/answer separation.

- [x] Record explicit approval of all 40 unchanged labels as SRC-011 and data/reviews/v1.0.json, bound to the candidate file SHA-256.
- [x] Add scripts/freeze_gold.py to create a versioned release or verify it with --check. An existing differing release must be preserved and rejected, not overwritten.
- [x] Export approved case records, separate input and answer files for each split, and snapshots of source, approval, and policy.
- [x] Create a manifest with versions, reviewer, IDs, split assignments, provenance, counts, and file hashes.
- [x] Test the exporter through its CLI: valid approval, missing approval, changed source, immutable existing release, repeatability, and exact model-input fields.
- [x] Review actual artifacts, update living docs, and record the local completion checkpoint.

Concrete files: data/reviews/v1.0.json, data/gold/v1.0/, scripts/freeze_gold.py, and tests/test_freeze_gold.py. Keep the original pending-candidate snapshot and its proposals unchanged; the separate review record owns the subsequent acceptance.

Validation commands: python scripts/freeze_gold.py --check; python scripts/check_candidates.py; python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check; python -m unittest discover -s tests -v. Check actual input keys are only case_id and transcript and that input/answer IDs match within each frozen split.

## Completion evidence

Completed 2026-11-05 after explicit owner approval of all 40 proposed labels as-is (SRC-011).

- AC01: REVIEW-001 identifies the human reviewer as project_owner and approves every source case ID. Gold records preserve expected labels, rationale, evidence, reviewer, date, and approval source.
- AC02: no corrections were requested. Original proposals remain unchanged in the historical candidate snapshot; the review ledger records subsequent acceptance.
- AC03: data/gold/v1.0/manifest.json freezes 40 cases, 20 families, grouped 20/20 splits, policy/dataset versions, approval provenance, and artifact hashes. Approval is bound to both candidate source and accepted policy hashes.
- AC04: the two classifier-input files contain exactly case_id and transcript. Expected labels and review metadata are separate. File-level isolation is verified; future runtime integration still needs its own checks.

All 22 tests passed, including the policy-binding regression that failed before the fix. Independent review confirmed the fix and checked actual final hashes, byte lengths, and both 20-case input contracts. The uncommitted pre-review output was preserved under ignored scratch storage before regenerating the corrected final artifact; no published release was overwritten.

Human approval and gold freeze are complete. No model, audio, UI, or application evaluation has run. Next step: choose the baseline model and implementation approach, then specify text-classification behavior and evaluation.
