# F-004: Local model pipeline requirements

Owner and acceptance owner: project owner.
Product requirements: PRD-R001 through PRD-R010.
Sources: SRC-012 through SRC-016 in the [source register](../../../intake/README.md).
Dependencies: completed F-001 through F-003; frozen gold v1.0.
Status: active. Batches 1 and 2 implement diagnostics, contracts, and selected text classification. Batch 3 implements evaluation and has a preserved first development baseline; fresh text-v2 evaluation and candidate freeze remain open. F-006 owns the implemented text workspace. SRC-024 defers audio and transcription to the [roadmap](../../../docs/ROADMAP.md).

## Problem, users, and outcome

The owner needs a local text-based callback review demo on the existing laptop. A reviewer selects a classifier, inspects a transcript, and sees a callback recommendation with evidence. The owner can explain the decisions and reproduce an evaluation.

SRC-016 originally placed transcription in the build. SRC-024 supersedes that portion; the original instruction remains historical. No model quality is established by either instruction.

## Scope and exclusions

Deliver local runtime diagnostics, an explicit compatible-model registry, a text-classification baseline, and reproducible scoring. F-006 owns the text review workspace and API. Use the existing accepted policy and frozen gold.

The owner selected qwen3.5:4b-q4_K_M for callback classification under SRC-018. Audio upload, transcription, and paired-audio verification are future enhancements without a committed model or date.

The initial system processes one job at a time on this laptop. Downloads happen only through an explicit setup action, never as a side effect of classification.

Live calls, speech synthesis, automatic callbacks, CRM writes, cloud inference, hosted deployment, speaker diarization, and concurrent multi-user operation remain outside this feature.

## Acceptance criteria

| ID | Observable outcome | Boundary or failure case |
| --- | --- | --- |
| F-004-AC01 | A diagnostic command reports Ollama connectivity, version, and installed models. | A stopped server, timeout, or empty model list produces an actionable status; no inference is implied. |
| F-004-AC02 | A reviewer selects a compatible classification model. | Missing or incompatible models disable classification. No silent downloads, cloud fallback, or invented classifier default. Independent transcription selection is deferred to the roadmap. |
| F-004-AC03 | Text input produces a validated callback outcome, rule references, explanation, and evidence from the selected transcript version. | Malformed output, unknown rules, absent evidence, empty input, and excessive input become explicit failures; input is never silently truncated. |
| F-004-AC04 | Processing failures remain distinguishable from all three policy outcomes. | A timeout or invalid output never becomes no_callback or an implicit needs_review label. Audio failure behavior is deferred with the audio enhancement. |
| F-004-AC05 | A run records model identity, runtime, settings, prompt and policy versions, transcript version and hash, timing, and status. | Changing text or model settings creates a new run; earlier evidence stays bound to its original input. |
| F-004-AC06 | Development scoring includes all cases, a three-outcome confusion matrix, callback recall and precision, review rate, unsafe misses, and processing failures. | Failures remain in total coverage; undefined metrics display their denominator and are not fabricated as zero or perfect. |
| F-004-AC07 | Held-out scoring uses a frozen configuration and separate input and answer files. | Expected labels never enter inference requests; held-out results do not guide tuning under the same claimed evaluation. |
| F-004-AC08 | Deferred to the roadmap: an uploaded fictional recording produces inspectable text using a transcription model. | Audio validation and silence behavior require future feature requirements and evidence; this criterion is not completed. |
| F-004-AC09 | Transferred to F-006-AC03 and AC05: versioned text editing and separate human decisions. | F-006 owns browser/API acceptance and preserves the original invariant. This row is not independently accepted or silently dropped. |
| F-004-AC10 | Deferred to the roadmap: paired audio comparison separates transcription differences from decision differences. | Actual laptop behavior and quality require future measurement; this criterion is not completed. |

## Open decisions

D-003 is narrowed in the [brief](../../../intake/PROJECT_BRIEF.md). SRC-018 resolves the classifier choice and authorizes explicit provisioning plus development-only inference. Batch 3 owns formal scoring and held-out configuration freeze. [F-006 requirements](../../completed/F-006-text-review-workspace/01_REQUIREMENTS.md) own text UI selection and browser/API acceptance. SRC-024 defers the audio portions of AC02, AC08, and AC10 to the roadmap.

D-004 remains open for numeric quality and latency targets. Functional acceptance requires the behaviors above; it does not establish production suitability. D-005 hosting is outside this local feature.

## Related documents

- [Technical specification](02_TECHNICAL_SPEC.md).
- [Implementation plan](03_IMPLEMENTATION_PLAN.md).
