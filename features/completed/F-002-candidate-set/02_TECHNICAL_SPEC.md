# F-002: Candidate data specification

Requirements: [feature requirements](01_REQUIREMENTS.md).

## Data format

Use one JSON object per line. Required fields are case_id, family_id, suggested_split, source, transcript, proposed_label, rule_ids, rationale, evidence, review_status, reviewed_label, and reviewer.

Labels are callback_required, no_callback, and needs_review. Suggested splits are development and evaluation. Source is synthetic. Rule IDs come from the accepted callback policy.

Pending records have null reviewer and reviewed_label. Approved records require both an identified reviewer and a valid reviewed_label. Rejected records remain excluded from gold. The validator checks metadata consistency, not the identity or independence of a claimed reviewer.

## Owning files

- `data/candidates/v0.1/cases.jsonl` owns candidate records.
- `data/candidates/v0.1/REVIEW.md` presents the same records to a person.
- `scripts/check_candidates.py` validates the file through a CLI.
- `scripts/render_candidate_review.py` generates REVIEW.md and checks it for drift with --check. It refuses to overwrite its candidate input.
- `tests/test_check_candidates.py` exercises the CLI on disposable candidate files.

The validator performs no model calls, file rewrites, or gold promotion. It reports errors with line numbers and exits nonzero for an invalid set. It checks required field types, allowed values, unique case IDs, verbatim evidence, grouped splits, duplicate transcripts, and review metadata.

## Risks

Synthetic examples have limited realism. Agent-proposed labels need human review. A structural pass is not a semantic evaluation. Evaluation examples and their expected labels must stay outside future classifier prompts.

No application framework or persistence architecture is selected by this format.

Next: [implementation plan](03_IMPLEMENTATION_PLAN.md).
