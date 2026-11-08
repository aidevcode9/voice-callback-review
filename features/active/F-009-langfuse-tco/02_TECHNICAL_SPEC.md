# F-009: Technical specification

Requirements: [requirements](01_REQUIREMENTS.md).

The shared classifier is the instrumentation boundary for the CLI, API worker, and evaluation. Trace a run as one span with a nested generation for the Ollama chat call. Capture only operational metadata, model ID, elapsed time, outcome and available token counts; omit transcript, prompt, evidence, case IDs, and raw errors. Langfuse is opt-in via environment configuration. Telemetry exceptions must not affect inference. Local Ollama remains the inference provider; the external Langfuse destination receives only the explicitly described telemetry.

Use the current Langfuse SDK where compatible. The project supports Python 3.10, while SDK 5 requires Python 3.11 or later; tracing is an optional integration on Python 3.11+ so the existing core remains supported. Use a separate dependency lock for the optional integration. Credentials stay in local ignored files or environment variables, never application records or source control.

The worksheet separates editable unknown assumptions from computed monthly, annual, and per-call totals. Local hardware and energy, labor, hosting, services, storage and transcription must be included; there is no assumed token price for local inference.

Verification covers disabled and enabled paths, private data exclusion, failures, counts, and actual trace ingestion using fictional input if the configured server is reachable. Model-quality evaluation and hosted deployment remain separate.
