# F-002: Implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).

## Workflow and ownership

Orchestrator: project-workflow.
Execution workflow: house planning-workflows for bounded data preparation, supported by pstack technical-writing and unslop.
Alternative inspected: pstack Feature. Its competing application designs and delegated implementation are not needed for this fixed data contract; the useful review and verification practices remain required.

One writer owns candidate files and validation code. A separate read-only review can inspect semantic consistency independently. F-001 is the blocking first step.

## Checkpoints

- [x] F-001 has completed documentation acceptance.
- [x] Create synthetic candidate JSONL and a matching readable packet.
- [x] Add the structural validator and behavior tests.
- [x] Run the validator and tests; review labels against the accepted policy.
- [x] Record limitations and the human-review handoff.

## Validation

- `python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl`: valid structure, no cross-split families or duplicates, evidence present, and 40 pending candidates.
- `python -m unittest discover -s tests -v`: valid data passes and invalid inputs fail for the intended reasons.
- Inspect the packet against JSONL and the policy. Resolve any reviewer finding.

## Completion evidence

Completed preparation on 2026-11-05.

- F-002-AC01: 40 synthetic records with policy references and verbatim evidence.
- F-002-AC02: all 40 remain pending; reviewer and reviewed_label are null. The review renderer's --check command confirms packet consistency.
- F-002-AC03: 20 families stay in a single suggested split; no duplicate transcripts; both splits contain all labels. Each split has 20 candidates.
- F-002-AC04: the validator passed on the actual file and all 12 CLI behavior tests passed, including evidence, duplicate IDs, split leakage, review metadata, and protection against rendering over the input.
- F-002-AC05: independent agent QA reviewed all 40 labels, rule references, and quotes with no actionable mismatch. The next human-review feature is specified separately.

Proposed label counts: 16 callback_required, 14 no_callback, 10 needs_review. These are not gold counts or model results.

The validator, renderer consistency check, and tests all passed. Human label review, gold freeze, application behavior, transcription, and model quality have not been verified. No deployment applies to this preparation feature.
