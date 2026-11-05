# F-002: Prepare callback-label candidates

Owner: agent for preparation; user for human label acceptance.
Product requirements: PRD-R003, PRD-R004, PRD-R006, and PRD-R007.
Dependency: F-001 accepted policy and labeling procedure.

## Outcome

Create a reviewable synthetic candidate set before implementing the model. The proposed defaults are 40 English-language cases in 20 families, split into 20 development and 20 evaluation candidates with each family in one split.

The feature prepares candidates. It does not approve their labels, freeze gold, implement the application, or run an AI model.

| Acceptance ID | Observable criterion |
| --- | --- |
| F-002-AC01 | JSONL contains 40 fictional cases with stable IDs, policy references, verbatim evidence, and proposed labels. |
| F-002-AC02 | All cases start pending with no reviewed label or reviewer. The Markdown packet matches the JSONL. |
| F-002-AC03 | Families and identical transcripts do not cross splits; all three outcomes occur in both suggested splits. |
| F-002-AC04 | A repeatable CLI validates the set and rejects malformed data, unsupported evidence, and invalid review metadata. |
| F-002-AC05 | The handoff identifies the remaining human review and gold-freeze work without claiming model accuracy. |

## Related documents

- [Technical specification](02_TECHNICAL_SPEC.md).
- [Implementation plan](03_IMPLEMENTATION_PLAN.md).
