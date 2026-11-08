# F-009: Langfuse tracing and cost worksheet

The owner requested Langfuse tracing and a total-cost-of-ownership worksheet. The review desk and CLI use the same local classifier; model inference remains local.

## Acceptance criteria

- F-009-AC01: An opt-in trace describes each classifier run and its model generation, token usage when provided, and success or failure without exporting transcripts, evidence, or credentials.
- F-009-AC02: Missing configuration, an unavailable SDK, or a telemetry failure does not change classification results; tracing can be disabled.
- F-009-AC03: Setup explains configuration and verifies an actual synthetic trace when connectivity permits. No held-out data is transmitted.
- F-009-AC04: A usable TCO worksheet calculates monthly, annual, and per-call costs from clearly identified editable assumptions, without presenting unknown costs as measured facts.

Hosted deployment, real customer data, model quality acceptance, and changes to the frozen evaluation set are outside scope.
