# F-002: Implementation plan

Read [requirements](01_REQUIREMENTS.md) and [technical specification](02_TECHNICAL_SPEC.md).

## Workflow and ownership

Orchestrator: project-workflow.
Execution workflow: house planning-workflows for bounded data preparation, supported by pstack technical-writing and unslop.
Alternative inspected: pstack Feature. Its competing application designs and delegated implementation are not needed for this fixed data contract; the useful review and verification practices remain required.

One writer owns candidate files and validation code. A separate read-only review can inspect semantic consistency independently. F-001 is the blocking first step.

## Checkpoints

- [ ] F-001 has completed documentation acceptance.
- [ ] Create synthetic candidate JSONL and a matching readable packet.
- [ ] Add the structural validator and behavior tests.
- [ ] Run the validator and tests; review labels against the accepted policy.
- [ ] Record limitations and the human-review handoff.

## Validation

- `python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl`: valid structure, no cross-split families or duplicates, evidence present, and 40 pending candidates.
- `python -m unittest discover -s tests -v`: valid data passes and invalid inputs fail for the intended reasons.
- Inspect the packet against JSONL and the policy. Resolve any reviewer finding.

## Current state

Specification prepared. Candidate data and validation have not yet been created. Human labels and model evaluation are outside this feature's completion claim.
