# Architecture

Current state: policy documents, synthetic candidates, an explicit human-approval ledger, frozen gold v1.0, and offline validation/export tools. F-004 batches 1 and 2 add diagnostics, local text classification, and exclusive JSON run records. Batch 3 adds isolated evaluation artifacts and offline scoring. F-006 adds the Next.js Review desk, FastAPI/SQLite persistence and Nginx single-origin routing. Audio is a future roadmap enhancement; hosting remains undecided. The first diagram describes the current text workflow.

```mermaid
flowchart LR
    Reviewer["Service reviewer"] --> UI["Review dashboard"]
    UI --> Input["Input handling"]
    UI --> Models["Compatible configured model choices"]
    Models -->|Classifier choice| Evaluate
    Input -->|Supplied text| Transcript["Versioned transcript"]
    Transcript --> Evaluate["Callback evaluator"]
    Evaluate -->|Processing error| UI
    Evaluate --> Prediction["Model recommendation, reason, and evidence"]
    Prediction --> UI
    UI --> Human["Separate reviewer decision"]
```

Text classification uses Ollama and records runtime, model identity, and settings. The classifier requests unloading after each run. Speech-to-text is unimplemented and deferred to the [roadmap](ROADMAP.md). See [local model options](LOCAL_MODEL_OPTIONS.md).

The callback evaluator receives the transcript version selected for the decision. Evidence must point to that version. Original text, a corrected version, the model recommendation, and the reviewer decision remain distinguishable.

Golden labels are part of a separate [evaluation flow](EVALUATION.md). They do not enter classifier inputs.

Optional [Langfuse tracing](LANGFUSE.md) records the submitted transcript, validated decision, and operational metadata from the shared classifier for CLI, review-desk, and evaluation runs. An environment setting restricts traces to metadata. Evaluation traces include their run ID, split, dataset version, and case ID for correlation; expected answers remain local. The system prompt and raw model response are not exported. Telemetry is disabled by default and does not replace local provenance.

## Strict external contracts

Classifier instructions are a version-selected package resource under src/voice_callback/prompts. classify.py assembles them with the separate accepted policy and generated response schema; the transcript stays a separate JSON user message. The package and evaluation source fingerprint include prompt text assets. [Classifier prompts](CLASSIFIER_PROMPTS.md) documents version changes and compatibility checks. Mechanical v2 extraction preserves its rendered prompt hash while changing source identity.

contracts.py defines strict Pydantic registry, classifier settings, input, response, saved-run, and prediction models. evaluation_contracts.py defines configuration, completion, report, and freeze artifacts. Extra fields and scalar coercion are rejected. The existing bounded JSON decoder rejects duplicate keys and non-finite values before strict Pydantic JSON validation; LF-only JSONL parsing preserves Unicode transcript separators. Validators preserve exact text, accepted policy-rule combinations, and verbatim transcript evidence.

```mermaid
flowchart LR
    JSON["External JSON or JSONL"] --> Decode["Bounded strict JSON decoding"]
    Decode --> Contracts["Strict Pydantic boundary models"]
    Contracts --> Domain["Immutable internal values and pure scoring"]
    Response["CallbackOutput model"] --> Schema["Generated Ollama response schema"]
    Response --> Contracts
    Domain --> Records["Validated exclusive run and evaluation artifacts"]
```

Internal dataclasses and the pure scorer remain independent of the UI and provider SDKs. CallbackOutput is the authoritative response contract used for both validation and schema generation. Rule consistency and exact evidence checks remain application validation after generation; a valid schema does not establish semantic truth or deterministic inference. callback-text-v2 records the generated schema's prompt change. System snapshots include the contract and Pydantic/core versions, and prior artifacts retain their original hashes and source identity.

The [F-004 specification](../features/active/F-004-local-model-pipeline/02_TECHNICAL_SPEC.md) owns the Python/Ollama classifier; [F-006](../features/completed/F-006-text-review-workspace/02_TECHNICAL_SPEC.md) owns the implemented Next.js frontend, FastAPI API and Nginx routing. The owner selected qwen3.5:4b-q4_K_M under D-003 in the [brief](../intake/PROJECT_BRIEF.md). Audio and GPU handoff are future concerns; deployment is outside this feature.

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

The implemented exporter validates approval against both the candidate and policy hashes and preserves an existing differing release.

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

Configured capabilities do not prove installation or inference. Faster-whisper availability is explicitly unverified. The selected classifier has an explicit configuration ID; every submission must select it explicitly. No implicit classifier default is inferred. See [local setup](LOCAL_SETUP.md) for executable commands, state meanings, and limits.

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

## Implemented batch 3 evaluation

```mermaid
flowchart LR
    CLI["evaluate CLI"] --> Split["datasets.py validates manifest and input-only split"]
    Split --> Config["evaluation_config.py snapshots the exact local system"]
    Config --> Runner["evaluate.py invokes existing classifier per case"]
    Runner --> Records["Exclusive run records and closed predictions"]
    Records --> Marker["Inference completion and integrity hashes"]
    Marker --> Answers["Separate reference-answer read"]
    Answers --> Scorer["scoring.py computes counts and explicit denominators"]
    Records --> Scorer
    Scorer --> Report["Immutable report and offline rescore"]
    Report --> Freeze["Explicit candidate freeze for later held-out use"]
```

json_io.py supplies strict duplicate/non-finite rejection and LF-only JSONL parsing to both classification and evaluation. classify.py exposes pure request construction with prompt/request hashes so evaluation reuses the actual classifier configuration. There is no second classifier prompt. Scoring depends on typed predictions and reference answers, not on Ollama or a UI. Inference completion is persisted before the scorer can open answers. Configuration drift or incomplete inference leaves inspectable artifacts without a quality report. Held-out execution requires a matching frozen system and explicit opt-in.

## Text workspace boundary (SRC-020, implemented by F-006)

```mermaid
flowchart LR
    Browser["Reviewer browser"] --> Nginx["Nginx — one local origin"]
    Nginx -->|pages / assets| Next["Next.js A Review desk"]
    Nginx -->|/api/v1| API["FastAPI boundary"]
    API --> Jobs["Single-job admission and local workspace records"]
    Jobs --> Core["Existing Python classifier / contracts / run storage"]
    Core --> Ollama["Existing loopback Ollama"]
```

The API reuses the core rather than cloning prompts or scoring. [F-006 contracts](../features/completed/F-006-text-review-workspace/02_TECHNICAL_SPEC.md) define implemented asynchronous jobs, idempotency, limits, crash recovery and case/version/review storage. Selector changes do not run inference. Held-out inputs/answers and freeze operations are excluded from this workspace. Static prototypes remain historical simulations. Hosting is undecided and deployment is outside scope.

## Implemented F-006 local workspace

```mermaid
flowchart LR
    Local["Local HTTP client — 127.0.0.1:8000"] --> API["Implemented FastAPI boundary"]
    API --> Store["Implemented SQLite workspace — versions/runs/reviews"]
    API --> Jobs["Implemented single background worker"]
    Jobs --> Lock["Shared CLI/API OS admission + crash marker"]
    Lock --> Core["Existing Python classifier/contracts"]
    Core --> Runtime["Local Ollama — no live check in this batch"]
    Web["Implemented Next.js A Review desk"] --> Proxy["Nginx — 127.0.0.1:8080"]
    Proxy -->|/api| API
    Proxy -->|pages/assets| Web
```

Source ownership and exact API deviations are recorded in F-006. Workspace results retain the existing strict run JSON inside append-only SQLite records; CLI artifacts/evaluation remain separate. Atomic transactions, immutable-history triggers and shared process admission protect explicit submissions. Production-stack browser checks cover explicit requests, editing/history/reviews, reconnect/restart, runtime failures and desktop/narrow accessibility. The Ollama endpoint is a controlled fixture; no model-quality result follows. The static prototypes remain simulations.
