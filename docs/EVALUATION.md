# Text evaluation

Status: batch 3 implements a development runner, immutable artifacts, deterministic offline scoring, and candidate configuration freezing. The first development baseline matched all 20 reference labels. Strict Pydantic boundary contracts are implemented and verified offline; a fresh development baseline now precedes candidate freeze. The frozen release has 20 development and 20 held-out evaluation cases. The [PRD](PRD.md) owns the rubric and acceptance decisions.

## Development checkpoint before contract migration

The owner ran evaluation 7f31782d-c234-4937-85fe-252add830d39 on clean commit 1f94357 with callback-text-v1 and the selected Qwen digest. Offline rescore reproduced 20/20 valid and correct outputs: callback recall 8/8, precision 8/8, needs-review rate 6/20, and no processing failures or unsafe misses. Original reports remain in the ignored reports/text directory; their hashes and full revision are recorded in the [implementation plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md). Copy that directory separately when preserving evidence across machines; ignored artifacts are not included in the Git commit.

One fictional development trial establishes neither held-out quality nor repeatability. Preserve that evidence. The approved strict Pydantic contract migration has passed offline checks. Commit the verified implementation and run a fresh development baseline before configuration freeze. The generated response schema requires callback-text-v2 and a new prompt/source fingerprint. Existing reports are not rewritten or presented as migrated runs; offline rescoring uses the original matching source revision.

## Run development inference before scoring

Run the canonical packaged workflow from the repository root:

```powershell
.venv\Scripts\python.exe -m voice_callback.cli evaluate --model qwen35-4b
```

The development split is the default. This command prepares a verified clean
checkout of the current commit, calls the shared classifier, saves predictions,
automatically scores them, and creates a self-contained `review.html` beside
`report.json`. It prints per-case progress to stderr and a readable summary to
stdout. Add `--json` for the machine-readable report. Commit source, registry,
policy and dataset changes first: relevant dirty or untracked inputs are rejected
rather than silently evaluating an older version. Outputs and the shared inference
lock stay in this repository's `reports/text` and `runtime/inference` directories.
No model is downloaded and the current command never automatically runs held-out.

Use `--prepare-only` to prepare the checkout without inference or telemetry. The
old `scripts/run_development_evaluation.py` is only an argument adapter; it now
requires the same explicit `--model` and has no separate setup or tracing policy.

Tracing is optional. The workflow reads supported settings from root `.env`, then
applies process environment values (including explicit empty values), then command
overrides. `--trace` enables it, `--no-trace` disables it, and `--metadata-only`
excludes transcript/decision content. Missing credentials or SDK do not block the
underlying evaluation; trace delivery is a separate observation. See
[Langfuse setup](LANGFUSE.md). Credentials are not stored in run artifacts or argv.
Keep non-secret model settings in `config/models.json`; no YAML profile is needed.

```powershell
.venv\Scripts\python.exe -m voice_callback.cli evaluate --model qwen35-4b --trace --metadata-only
.venv\Scripts\python.exe -m voice_callback.cli evaluate --model qwen35-4b --baseline reports/text/BASELINE_ID
.venv\Scripts\python.exe -m voice_callback.cli evaluations
.venv\Scripts\python.exe -m voice_callback.cli evaluations --run-dir reports/text/RUN_ID
.venv\Scripts\python.exe -m voice_callback.cli evaluations --run-dir reports/text/RUN_ID --baseline reports/text/BASELINE_ID
```

`evaluations` lists development runs, including incomplete/invalid states. Selecting
`--run-dir` validates and renders a saved completed development report with no
inference or telemetry. The report shows all cases, approved answers, predictions,
reasons, evidence, transcripts, confusion counts, failures and source identity.
Inputs with held-out declarations are refused before loading their data/answers.
Interrupted runs keep partial artifacts and no completed report; the run path and
runtime recovery instructions remain visible in progress output and history.

Comparison validates the selected baseline before new inference. Dataset version,
manifest/input/answer hashes, exact case/transcript coverage, scorer version and
metric definitions must match. Model, prompt, settings and code can differ; those
changes are displayed. Fixes, regressions, unsafe misses and metric fractions/deltas
are paired by case. Undefined metrics have no numeric delta. Reports infer no
acceptance threshold. A baseline comparison is not a repeatability or statistical
significance claim.

Saved-snapshot review checks artifact/provenance integrity and callback-score-v1
count consistency. It does not rerun historical source. Existing `score` still
requires the original matching source fingerprint. Original `report.json` bytes
and baseline artifacts are never rewritten; baseline-specific HTML is additive.
Historical artifact formats unsupported by the strict contracts are rejected
explicitly rather than migrated. See [F-011](../features/completed/F-011-evaluation-workflow/01_REQUIREMENTS.md).

The runner validates the frozen manifest, exact split IDs, and input-file hash. It reads only ID/transcript records before inference. Each case gets a classification run with its original input version/hash, the selected model identity/settings, and prompt/policy provenance. No answer, rationale, or expected label enters the model request.

When [Langfuse tracing](LANGFUSE.md) is enabled, each case also produces a trace labeled with the evaluation ID, split, dataset version, and case ID. The normal content setting controls whether the input transcript and model decision are sent. Expected answers and scoring reports remain local. The held-out split still requires a frozen configuration and separate owner authorization; tracing an authorized held-out run can send its inputs and predictions to the configured Langfuse service.

```mermaid
flowchart TD
    Manifest["Frozen manifest and input hashes"] --> Inputs["Input-only split snapshot"]
    System["Explicit model, policy, prompt, runtime, code identity"] --> Predict["Local classification of every input"]
    Inputs --> Predict
    Predict --> Runs["Exclusive per-case success or failure records"]
    Runs --> Predictions["Closed predictions.jsonl and integrity hashes"]
    Predictions --> Complete["Inference-complete marker"]
    Complete --> Answers["Scorer opens separate expected answers"]
    Answers --> Score["Exact case join and deterministic counts"]
    Predictions --> Score
    Score --> Report["Exclusive report.json"]
```

A unique directory under reports/text contains configuration.json, evaluation.json, inputs.jsonl, runs/, predictions.jsonl, inference-complete.json, and report.json. All writes preserve prior artifacts. Interrupted inference retains its partial files and an aborted.json marker; it cannot be scored. Configuration drift prevents a completed report. A missing model is never downloaded automatically.

The report records dataset/manifest/input/answer/prediction/system hashes, scorer version, one trial, all-case totals, and inspectable disagreements. A configuration snapshot records the model digest and metadata hash, explicit settings, server version/URL/timeouts, prompt/policy versions and hashes, Git revision/clean state, and Python source-byte fingerprint. Changing code or data prevents silent reuse under the same claimed system.

## Interpret the denominators

| Result | Definition |
| --- | --- |
| Confusion matrix | Three expected-outcome rows by three valid predicted-outcome columns. Processing failures are reported separately by expected label. |
| Strict callback recall | Correct callback predictions divided by all expected callbacks, including cases that failed processing or returned needs_review. |
| Callback precision | Correct callback predictions divided by all valid callback predictions. |
| Needs-review rate | Valid needs_review predictions divided by all input cases, including processing failures. |
| Valid-output coverage | Validated predictions divided by all input cases. |
| Unsafe misses | IDs where callback_required was predicted no_callback. |

Each metric includes its numerator, denominator, and value. A zero denominator produces null, never an invented zero or perfect value. Every frozen input must have exactly one prediction or processing failure. Missing, duplicate, or foreign records are rejected before scoring. Processing failures never become a fourth policy outcome or an implicit needs_review.

The labels are independently owner-approved references. Validation checks output structure and exact evidence locations; it does not prove semantic correctness. Preserve disagreements and inspect their reasons. Do not rewrite a reference merely because a model disagrees. Label corrections require a new dataset version.

## Rescore without inference

```powershell
.venv\Scripts\python.exe -m voice_callback.cli score --run-dir reports/text/RUN_ID
```

Replace RUN_ID with the directory printed by evaluate. Offline scoring verifies completion, coverage, hashes, per-case run bindings, and the source fingerprint before opening answers. An identical report is verified without rewriting it; a differing report is preserved and reported as an error. No model call occurs. Exit 0 means all inputs have valid outputs, exit 1 means a completed report contains processing failures or an I/O/runtime operation failed, and exit 2 means invalid configuration or artifact validation. Incorrect policy predictions remain visible disagreements even when execution exits 0.

## Freeze a candidate before held-out inference

```powershell
.venv\Scripts\python.exe -m voice_callback.cli freeze-evaluation --run-dir reports/text/RUN_ID
```

Freeze requires a complete development report without processing failures, an originally clean committed implementation, and unchanged Python source in a currently clean Git revision. It writes an exclusive frozen-configuration.json bound to the development report, full system snapshot, dataset manifest, and current Git revision. Freezing is reproducibility preparation, not quality acceptance. Use --output to name another artifact rather than replacing a differing freeze.

The held-out path requires both --frozen-config and --allow-held-out with --split evaluation. It also requires the exact frozen code revision/source, model digest and metadata, prompt/policy, settings, runtime, and dataset manifest. Tests exercise this path with a separate synthetic fixture. No real held-out inference is part of the current authorization; the owner selects that action separately after the candidate is frozen.

## Limits of the first baseline

The planned first baseline is one trial of one selected model over 20 fictional development cases, with related conversations grouped together. Report counts alongside fractions. The run can reveal functional failures and development disagreements, but it cannot establish a repeatability spread, a model comparison, a population accuracy estimate, or a performance target. D-004 remains open for the owner's acceptance threshold. A successful small development run is not production approval.

## Future enhancement: paired audio evaluation

```mermaid
flowchart LR
    Pair["Proposed paired fictional audio and reviewed transcript"] --> Reference["Reference text"]
    Pair --> Audio["Recorded audio"]
    Audio --> STT["Proposed transcription stage"]
    Reference --> TextRun["Fixed classifier on reference text"]
    STT --> AudioRun["Same classifier on transcribed text"]
    TextRun --> Compare["Separate transcription differences and decision changes"]
    AudioRun --> Compare
```

SRC-024 defers transcription and paired checks to the [roadmap](ROADMAP.md). This diagram is a future proposal, not a current F-004 acceptance gate. The iterative workspace excludes held-out cases and answers; it does not invoke freeze or held-out evaluation. Gold v1.0 remains unchanged.

## Transport uncertainty and admission

F-006 shares inference admission across CLI/API entrypoints. Evaluation now stops after a timeout/unavailable/HTTP/invalid-transport failure, preserving that failed run/prediction plus aborted.json without a completion marker or quality report. It opens no answers and does not send another case while provider execution is uncertain. Known terminal failures such as validated invalid model output can still be included in a completed report and its denominators. Pure metric definitions are unchanged. After stopping/restarting the runtime, explicitly recover admission before a new run; never infer quiescence from a timestamp or closed client connection. Historical baseline artifacts remain unchanged and require their original source for rescore.

## Evaluation admission observation

The CLI evaluation lease observes each classifier result before persistence or provenance checks. A timeout therefore retains recovery admission even if configuration drift makes later validation fail. Library callers that hold an InferenceLease should bind evaluate's observe_result parameter to lease.observe; the shared CLI does this. Unknown provider completion still aborts before another request or answer read.
