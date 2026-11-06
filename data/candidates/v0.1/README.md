# Synthetic callback candidates v0.1

Status: historical 40-case candidate snapshot. Its pending fields are intentionally preserved. Later owner approval is recorded in [REVIEW-001](../../reviews/v1.0.json), and accepted labels are frozen in [gold v1.0](../../gold/v1.0/README.md).

- [cases.jsonl](cases.jsonl) owns the candidate records.
- [Review packet](REVIEW.md) displays the same transcripts and proposed answers.
- [Accepted policy](../../../docs/CALLBACK_POLICY.md) defines label meanings.
- [Label guide](../../../docs/LABEL_GUIDE.md) defines review and gold-release requirements.

The starter has 20 scenario families with two related variants each. Suggested development and evaluation splits each contain 20 cases; a family stays within one split. Proposed labels total 16 callback_required, 14 no_callback, and 10 needs_review.

These cases are fictional administrative conversations. Owner approval is recorded separately from the original proposals. The set does not establish operational representativeness or model accuracy.

## Preserve this source snapshot

The owner approved these labels unchanged. Keep this source file intact so the approval hash remains reproducible. Corrections require a new candidate/review version and a new gold release. The procedure below describes annotation fields for future candidate versions.

## Review future candidates

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
