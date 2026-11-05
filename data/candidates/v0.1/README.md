# Synthetic callback candidates v0.1

Status: 40 agent-authored candidates, all pending human review. No gold release exists.

- [cases.jsonl](cases.jsonl) owns the candidate records.
- [Review packet](REVIEW.md) displays the same transcripts and proposed answers.
- [Accepted policy](../../../docs/CALLBACK_POLICY.md) defines label meanings.
- [Label guide](../../../docs/LABEL_GUIDE.md) defines review and gold-release requirements.

The starter has 20 scenario families with two related variants each. Suggested development and evaluation splits each contain 20 cases; a family stays within one split. Proposed labels total 16 callback_required, 14 no_callback, and 10 needs_review.

These cases are fictional administrative conversations. The language, size, suggested split, and nominated reviewer are preparation defaults, not claims of operational representativeness or user-approved gold data.

## Review the data

Read a transcript independently, record your reviewed label and reviewer identity in JSONL, and resolve disagreements using the policy. Use review_status approved only after a human has reviewed the record. Rejected records require an identified reviewer and a null reviewed_label. Pending records keep both fields null.

The validator checks format and metadata, not semantic correctness or who actually performed a review. A gold release needs a separate reviewed manifest and version.

## Reproduce the packet and checks

```powershell
python scripts/check_candidates.py data/candidates/v0.1/cases.jsonl
python scripts/render_candidate_review.py data/candidates/v0.1/cases.jsonl --check
python -m unittest discover -s tests -v
```

Run these commands from the repository root. To regenerate the packet after editing JSONL, run the renderer without --check. It replaces the generated REVIEW.md; keep human review data in JSONL.

Expected labels and reviewer notes must not enter future classifier prompts. Suggested evaluation cases become a frozen evaluation split only after review and a recorded release.
