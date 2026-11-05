# Label candidate calls

Apply [callback policy v1.0](CALLBACK_POLICY.md) to the whole transcript.

## Review one case

1. Read the transcript without relying on the proposed label.
2. Identify the final known issue state and any outstanding callback request or promise.
3. Select callback_required, no_callback, or needs_review under the accepted policy.
4. Record the applicable rule IDs, a short rationale, and verbatim evidence.
5. Compare with the proposed label. Correct it when the evidence and policy require a different answer.
6. Record the reviewer and reviewed label. Keep unclear labeling disputes pending until adjudicated.

An ambiguous call can have an accepted needs_review label. A pending annotation is a different state: nobody has accepted its label yet.

## Keep candidate and gold states separate

The agent may author fictional transcripts and propose labels. The project owner is the proposed human reviewer for the starter set. The owner can nominate another reviewer.

A pending candidate has no reviewer or reviewed label. An approved annotation requires an identified human reviewer, a reviewed label, rationale, and supporting evidence. Preserve the proposal and the review result separately.

A label dispute is resolved against the transcript and policy, not the candidate model's preferred answer. A policy gap returns to the owner. Do not make up missing context.

## Freeze a gold version

After human review, check case IDs, provenance, evidence, and grouped splits. Record the policy version and a dataset version with a manifest. Export only approved annotations into a gold release. Rejected or pending records stay outside that release.

The evaluation runner must supply only the allowed transcript input and case identifier to the callback evaluator. Expected labels and reviewer notes belong to the scorer. Do not use evaluation examples as prompt demonstrations.

Once evaluation is frozen, a justified correction creates a new version with the reviewer and reason recorded. Keep model and prompt versions attached to each run. A data-format validation pass does not establish that a label is correct or that a model works.
