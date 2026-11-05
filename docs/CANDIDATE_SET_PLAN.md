# Starter candidate-set plan

Status: preparation defaults proposed by the agent under the user's instruction to proceed. The callback policy is accepted; these dataset details are not recorded as user-approved.

## Size and review

Prepare 40 short fictional English-language transcripts in 20 scenario families, with two related variants per family. Nominate the user, the current acceptance owner, as human label reviewer. Another reviewer or a different size can be selected before gold is frozen.

Use a suggested 20-case development split and 20-case evaluation split. Keep each family wholly in one split. Ensure both splits contain callback-required, no-callback, and needs-review examples. These are candidate assignments until review and freeze.

Include unresolved issues, explicit requests, representative promises, resolved requests, wrong numbers, non-actionable spam, earlier unresolved issues resolved by the end, uncertainty, contradictions, and resolved issues with a separate outstanding callback obligation.

## Files and fields

Store candidates as JSONL under `data/candidates/v0.1/`. Each record has a stable case ID and family ID, suggested split, synthetic provenance, transcript, proposed label, rule IDs, rationale, evidence quotes, and a pending review state.

Human review adds an identified reviewer and reviewed label. Neither policy acceptance nor the agent's proposed answer makes a candidate gold.

A readable review packet should show the same cases as the JSONL. Validation checks shape, evidence quotes, IDs, review metadata, and split grouping. It cannot validate semantic label correctness.

## Next feature

[F-002](../features/backlog/F-002-candidate-set/01_REQUIREMENTS.md) prepares the candidate files, readable review packet, and repeatable validation. Human review and a frozen gold release remain separate deliverables.

No actual customer data, provider credentials, transcription service, or model call is needed for this preparation.
