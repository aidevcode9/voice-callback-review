# F-004: Local model pipeline requirements

Owner and acceptance owner: project owner.
Product requirements: PRD-R001 through PRD-R010.
Sources: SRC-012 through SRC-016 in the [source register](../../../intake/README.md).
Dependencies: completed F-001 through F-003; frozen gold v1.0.
Status: active. Batches 1 and 2 implement diagnostics, contracts, and selected text classification. Batch 3 implements evaluation and has a preserved first development baseline; strict contract migration precedes final freeze. Audio remains the final planned stage. Frontend/API scope and browser acceptance now belong to F-006 (SRC-020).

## Problem, users, and outcome

The owner needs a working local voice-classification demo on the existing laptop without paid API credentials. A reviewer chooses transcription and callback models, inspects the transcript, and sees a callback recommendation with evidence. The owner can explain the decisions and reproduce an evaluation.

SRC-016 places local runtime setup, model selection, transcription, and classification inside the build. It authorizes this plan; it does not select a deferred classifier or establish model quality.

## Scope and exclusions

Deliver local runtime diagnostics, an explicit compatible-model registry, a text-classification baseline, reproducible scoring, speech-to-text, with the text review workspace/API owned separately by F-006. Complete text review/testing before transcription and paired-audio integration, the final stage. Use the existing accepted policy and frozen gold.

Plan Whisper large-v3-turbo through faster-whisper as the first transcription candidate, with small as a selectable fallback. Confirm its actual GPU fit on a fictional recording. The owner selected qwen3.5:4b-q4_K_M for callback classification under SRC-018.

The initial system processes one job at a time on this laptop. It releases stage-specific GPU resources before loading the next stage when necessary. Downloads happen only through an explicit setup action, never as a side effect of classification or transcription.

Live calls, speech synthesis, automatic callbacks, CRM writes, cloud inference, hosted deployment, speaker diarization, and concurrent multi-user operation remain outside this feature.

## Acceptance criteria

| ID | Observable outcome | Boundary or failure case |
| --- | --- | --- |
| F-004-AC01 | A diagnostic command reports Ollama connectivity, version, and installed models. | A stopped server, timeout, or empty model list produces an actionable status; no inference is implied. |
| F-004-AC02 | A reviewer selects compatible transcription and classification models independently. | Missing or incompatible models disable the affected action. No silent downloads, cloud fallback, or invented classifier default. |
| F-004-AC03 | Text input produces a validated callback outcome, rule references, explanation, and evidence from the selected transcript version. | Malformed output, unknown rules, absent evidence, empty input, and excessive input become explicit failures; input is never silently truncated. |
| F-004-AC04 | Processing failures remain distinguishable from all three policy outcomes. | A timeout, transcription error, or invalid output never becomes no_callback or an implicit needs_review label. |
| F-004-AC05 | A run records model identity, runtime, settings, prompt and policy versions, transcript version and hash, timing, and status. | Changing text or model settings creates a new run; earlier evidence stays bound to its original input. |
| F-004-AC06 | Development scoring includes all cases, a three-outcome confusion matrix, callback recall and precision, review rate, unsafe misses, and processing failures. | Failures remain in total coverage; undefined metrics display their denominator and are not fabricated as zero or perfect. |
| F-004-AC07 | Held-out scoring uses a frozen configuration and separate input and answer files. | Expected labels never enter inference requests; held-out results do not guide tuning under the same claimed evaluation. |
| F-004-AC08 | An uploaded fictional recording produces inspectable text using the selected transcription model. | Unsupported, empty, oversized, or undecodable audio produces an error. Silent audio cannot invent a successful conversation. |
| F-004-AC09 | Transferred to F-006-AC03 and AC05: versioned text editing and separate human decisions. | F-006 owns browser/API acceptance and preserves the original invariant. This row is not independently accepted or silently dropped. |
| F-004-AC10 | A paired audio demonstration separates transcription differences from decision differences and records actual laptop behavior. | GPU memory failures remain visible. Audio quality and speed are reported only after measurement. |

## Open decisions

D-003 is narrowed in the [brief](../../../intake/PROJECT_BRIEF.md). The first batch can implement diagnostics and model-independent contracts now. SRC-018 resolves the classifier choice and authorizes explicit provisioning plus development-only inference. Batch 3 owns formal scoring and held-out configuration freeze. The transcription candidate requires dependency/hardware verification in the final stage. SRC-020 selects the Next.js/Nginx/proposed FastAPI direction; [F-006 requirements](../../completed/F-006-text-review-workspace/01_REQUIREMENTS.md) own UI model selection and browser/API acceptance. F-004-AC02 retains registry capability and final independent transcription selection; AC08/AC10 remain here.

D-004 remains open for numeric quality and latency targets. Functional acceptance requires the behaviors above; it does not establish production suitability. D-005 hosting is outside this local feature.

## Related documents

- [Technical specification](02_TECHNICAL_SPEC.md).
- [Implementation plan](03_IMPLEMENTATION_PLAN.md).
