# Architecture

Current state: policy documents, synthetic candidates, an explicit human-approval ledger, frozen gold v1.0, and offline validation/export tools. F-004 batches 1 and 2 add diagnostics, local text classification, and exclusive JSON run records. Evaluation, audio, dashboard, and deployment remain planned. The first diagram describes the proposed full application.

```mermaid
flowchart LR
    Reviewer["Service reviewer"] --> UI["Review dashboard"]
    UI --> Input["Input handling"]
    UI --> Models["Compatible configured model choices"]
    Models -->|Speech-to-text choice| STT
    Models -->|Classifier choice| Evaluate
    Input -->|Recorded audio| STT["Transcription adapter"]
    Input -->|Supplied text| Transcript["Versioned transcript"]
    STT -->|Successful text| Transcript
    STT -->|Processing error| UI
    Transcript --> Evaluate["Callback evaluator"]
    Evaluate -->|Processing error| UI
    Evaluate --> Prediction["Model recommendation, reason, and evidence"]
    Prediction --> UI
    UI --> Human["Separate reviewer decision"]
```

The adapters use independent model selections and record runtime, model identity, and settings per stage. Text classification is implemented through Ollama; speech-to-text remains unimplemented. The classifier requests unloading after each run. Sequential audio-to-text resource handoff remains a later integration check. See [local model options](LOCAL_MODEL_OPTIONS.md).

The callback evaluator receives the transcript version selected for the decision. Evidence must point to that version. Original text, a corrected version, the model recommendation, and the reviewer decision remain distinguishable.

Golden labels are part of a separate [evaluation flow](EVALUATION.md). They do not enter classifier inputs.

The [F-004 specification](../features/active/F-004-local-model-pipeline/02_TECHNICAL_SPEC.md) separates the implemented Python/Ollama classifier from proposed faster-whisper transcription and Streamlit dashboard. The owner selected qwen3.5:4b-q4_K_M under D-003 in the [brief](../intake/PROJECT_BRIEF.md). Audio dependencies and GPU handoff remain implementation checks; deployment is outside this feature.

Update this diagram when the implemented structure changes. Keep proposed components labeled until they exist.

## Implemented offline data flow

```mermaid
flowchart LR
    Candidate["Original candidate snapshot"] --> Export["Gold exporter"]
    Approval["Explicit human approval and hashes"] --> Export
    Policy["Accepted policy snapshot"] --> Export
    Export --> Inputs["Classifier inputs: ID and transcript only"]
    Export --> Answers["Separate expected answers"]
    Export --> Audit["Frozen manifest and audit snapshots"]
```

The application diagram above remains proposed. The implemented exporter validates approval against both the candidate and policy hashes and preserves an existing differing release.

## Implemented batch 1 diagnostics

```mermaid
flowchart LR
    CLI["doctor / models CLI"] --> Registry["Explicit config/models.json"]
    CLI --> Doctor["Ollama diagnostic adapter"]
    Doctor --> Version["GET /api/version"]
    Doctor --> Tags["GET /api/tags"]
    Registry --> Join["Stage capabilities + observed inventory"]
    Tags --> Join
    Join --> JSON["JSON availability and safe failures"]
    Version --> JSON
```

The package lives under src/voice_callback. domain.py defines transcript versions, stage-specific model configuration, immutable settings, three policy outcomes, run provenance, and distinct success/failure variants. models.py validates the registry and joins exact Ollama tags with observed digests. ollama.py restricts bounded HTTP requests to loopback; diagnostic commands remain read-only. cli.py renders JSON and exit codes. Business contracts do not depend on a UI or provider SDK.

Configured capabilities do not prove installation or inference. Faster-whisper availability is explicitly unverified. No classifier default is configured. See [local setup](LOCAL_SETUP.md) for executable commands, state meanings, and limits.

## Implemented batch 2 text classification

```mermaid
flowchart LR
    CLI["classify CLI with explicit model ID"] --> Input["Input-only JSONL or exact UTF-8 text"]
    Input --> Version["Transcript version and hash"]
    Policy["Hash-pinned accepted policy"] --> Prompt["Policy prompt and response schema"]
    Version --> Prompt
    CLI --> Verify["Local inventory, version, and model metadata"]
    Verify --> Chat["POST /api/chat, no truncation or retries"]
    Prompt --> Chat
    Chat --> Validate["Outcome, rules, reason, exact transcript evidence"]
    Validate --> Record["RunSuccess or RunFailure with provenance"]
    Record --> Store["Exclusive runtime/classifications JSON file"]
    Record --> Output["JSON stdout and process exit"]
```

classify.py owns prompt construction and validation. The transcript is data in a separate user message. Expected answers are rejected by the JSONL reader. storage.py serializes immutable domain values and creates each record exclusively. Model identity is checked before and after a successful inference. A malformed response, context overflow, timeout, or resource error cannot contain a successful policy label. Semantic correctness of otherwise valid reasons remains an evaluation question.
