# Set up local diagnostics and text classification

Run these commands in the voice-callback-review repository. Python 3.10 or later is required. Batch 1 was verified with Python 3.13.1 and pip 24.3.1 on Windows.

## Create the project environment

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --disable-pip-version-check --no-deps -e .
.venv\Scripts\python.exe -m pip check
```

The editable install uses the pinned setuptools 80.9.0 build backend in pyproject.toml. Pip may fetch that build dependency from the package index. The application has no third-party runtime dependencies. The virtual environment and generated package metadata are ignored by Git. Activation is optional when commands use the environment's interpreter explicitly.

Audio and dashboard dependencies are deferred to their implementation batches. Environment setup does not install faster-whisper or any model weights. The separately authorized Qwen provisioning step appears below. No provider SDK, API key, or sign-in is required.

## Inspect the local server and configured choices

Start your existing Ollama server if necessary, then run:

```powershell
.venv\Scripts\python.exe -m voice_callback.cli doctor
.venv\Scripts\python.exe -m voice_callback.cli models --stage classification
.venv\Scripts\python.exe -m voice_callback.cli models --stage transcription
```

The installed console entrypoint supports the same arguments:

```powershell
.venv\Scripts\voice-callback.exe doctor
```

All commands print JSON. An empty installed-model list exits with code 0 because the observation succeeded. It does not prove inference. On 2026-11-05, live checks reported Ollama 0.40.14, zero installed models, no configured classifier, and two unverified transcription candidates. The executable was absent from this process's PATH while the HTTP server was reachable.

The registry is [config/models.json](../config/models.json). Its entries declare capabilities and settings, not installation or a selected default. The entries are the owner-selected qwen35-4b classifier and planned large-v3-turbo and small transcription candidates. No default is selected by the registry; classify requires --model explicitly.

## Diagnose an unavailable choice

Read installed_models separately from configured_models. A model discovered in Ollama is never automatically added to the registry or chosen as a classifier. Ollama identity matching uses the exact configured tag, including its explicit version tag where supplied. Its observed digest is retained.

Configured entries report not_installed when the server's inventory lacks that model. They report installation_unknown when inventory retrieval fails. Faster-whisper entries report runtime_not_verified because batch 1 does not inspect or provision that runtime. Ollama-only transcription reports adapter_not_implemented. Known remote models report remote_not_supported.

The selectable field identifies a configured, stage-compatible local Ollama inventory match. It does not establish semantic suitability or successful inference. Diagnostic commands always report inference_verified as false because they perform no inference. The separate classify command verifies runtime and model metadata before executing.

If ollama_binary is null, the executable was not found on PATH. That field alone cannot establish whether Ollama is installed elsewhere. Server version, inventory retrieval, and executable discovery are independent observations.

Exit code 1 means a diagnostic request failed. Check failures for unavailable, timeout, http_error, or invalid_response. Start the local server or check its port, then rerun diagnostics. Unknown inventory is null rather than an empty list. A version may still be reported when model discovery fails. Exit code 2 means configuration or command arguments are invalid.

## Override diagnostic settings

```powershell
.venv\Scripts\python.exe -m voice_callback.cli doctor --url http://127.0.0.1:11434 --timeout 3 --registry config/models.json
```

Run from the repository root, or pass an explicit registry path. Only loopback HTTP at 127.0.0.1, localhost, or ::1 is accepted. Localhost connects directly to 127.0.0.1. Credentials, remote endpoints, redirects, URL paths, and cloud entries are rejected. HTTP proxy environment variables are not used.

Requests have a one-second connection limit and a three-second total limit by default, with a one-MiB response limit. The timeout option accepts finite values greater than zero and at most 30 seconds. Doctor makes two bounded requests without retries. It uses GET /api/version and GET /api/tags. It never calls inference, pull, or mutation endpoints.

The adapter follows the official [documentation index](https://docs.ollama.com/llms.txt), [version contract](https://docs.ollama.com/api-reference/get-version), [model inventory contract](https://docs.ollama.com/api/tags), and [HTTP error contract](https://docs.ollama.com/api/errors). Model capability verification through [show model details](https://docs.ollama.com/api-reference/show-model-details) belongs to the selected-classifier batch.

## Verify offline behavior and immutable data

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m unittest discover -s tests -p test_ollama.py -v
.venv\Scripts\python.exe -m unittest discover -s tests -p test_models.py -v
.venv\Scripts\python.exe scripts/freeze_gold.py --check
git diff --check
```

The behavior tests use controlled loopback HTTP servers and a controlled connection-refusal fixture. They need no running Ollama, downloaded models, or external network. Classification has offline tests and focused live development evidence. Evaluation now has offline behavior checks; transcription and UI execution remain planned in [F-004](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md).

## Development quality baseline

Install requirements-dev.txt with --require-hashes and run scripts/check_project.py for the full baseline. The [quality guide](QUALITY_CHECKS.md) records Ruff, Pyright, snapshot preflight, clean-wheel tests, and GitHub Actions. Those are development tools; the application still has no third-party runtime dependencies.

## Provision the selected classifier explicitly

The owner selected qwen3.5:4b-q4_K_M under SRC-018. Its initial package is about 3.3 GB. This is a separate download action, never a side effect of doctor, models, or classify. With the local Ollama server running, use its CLI if available:

```powershell
ollama pull qwen3.5:4b-q4_K_M
```

The server is reachable even when the executable is absent from this shell's PATH. The equivalent explicit setup action used on this laptop was:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:11434/api/pull -Method Post -ContentType application/json -Body '{"model":"qwen3.5:4b-q4_K_M","stream":false}' -TimeoutSec 1200
.venv\Scripts\python.exe -m voice_callback.cli models --stage classification
```

On 2026-11-06 the pull returned success. Ollama 0.40.15 reports the exact tag installed, GGUF/Q4_K_M, qwen35, completion, and thinking controls. The observed digest is d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04. A tag may later change; inspect the run's recorded digest. See the [classifier comparison](LOCAL_MODEL_OPTIONS.md) for the alternatives and memory limits.

## Classify one development transcript

```powershell
.venv\Scripts\python.exe -m voice_callback.cli classify --input data/gold/v1.0/inputs/development.jsonl --case-id VC-001 --model qwen35-4b
```

--model is a configuration ID from config/models.json, not a guessed default or arbitrary downloaded tag. Input-only JSONL rows must contain exactly case_id and transcript; expected-label fields are rejected. Use a UTF-8 .txt path with --case-id for other development text. Text and line endings are preserved exactly. The default transcript version is its SHA-256 hash; --transcript-version can supply a version ID.

The file limit is 1 MiB and the transcript limit is 12000 UTF-8 bytes. Empty or oversized text fails without a model call. The initial settings are num_ctx 8192, num_predict 768, temperature 0, seed 42, think false, and keep_alive 0. Ollama tokenizes the actual request and rejects context overflow through truncate false and shift false. No text is silently discarded. Ollama 0.40.15 or later is required for the inspected request contract. Output stopped by its token limit is invalid_output.

--timeout still controls short diagnostic/metadata requests. --inference-timeout defaults to 180 seconds and accepts a finite positive value up to 600. Connection setup is bounded by one second or the shorter applicable deadline. Response size remains capped at 1 MiB. There are no automatic retries or downloads. The request asks Ollama to unload the classifier after completion; audio-to-classifier memory handoff remains a later check.

Classification prints one JSON record to stdout and its saved path to stderr. Each run saves a new exclusive file under runtime/classifications, or --output-dir. Success has status success and a validated output. A processing failure has status processing_error and a failure without a policy label. Exit 0 means validated success, exit 1 means processing/storage failure, and exit 2 means invalid CLI input or registry configuration. An inability to save a record reports storage_error. Malformed model content is not echoed.

The record includes the exact model tag/digest and settings, server version and URL, case/transcript version/hash, prompt/policy version/hash, metadata/request hashes, UTC start, elapsed time, and either a validated decision or a typed failure. Prior records remain separate when text or settings change. These files are ignored local runtime artifacts. Structure and exact evidence validation do not prove that every statement in a reason is semantically correct.

Batch 2 development checks cover VC-001, VC-021, VC-025, VC-033, synthetic context overflow, and instruction-like transcript data. They are integration evidence, not a full development score or held-out result. No answer file is opened by classification. The [implementation plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) records observations. Batch 3 adds the evaluation commands below; audio and dashboard remain later work.

## Evaluate the development split

```powershell
.venv\Scripts\python.exe -m voice_callback.cli evaluate --split development --model qwen35-4b
```

This executes every development input using the explicit model, saves exclusive per-case runs and predictions, then opens the separate answers for scoring. The printed report path identifies reports/text/RUN_ID/report.json. The report includes confusion counts, strict callback recall, callback precision, needs-review rate, valid-output coverage, unsafe misses, failures, and disagreements. It states all denominators and uses null when a denominator is zero.

After the run, replace RUN_ID in these offline commands with its printed directory:

```powershell
.venv\Scripts\python.exe -m voice_callback.cli score --run-dir reports/text/RUN_ID
.venv\Scripts\python.exe -m voice_callback.cli freeze-evaluation --run-dir reports/text/RUN_ID
```

score verifies the saved artifacts and recomputes the same report without inference. freeze-evaluation requires a complete development baseline without processing failures and unchanged clean committed source. It binds a candidate snapshot to the current Git revision, model/prompt/policy/runtime/settings, dataset manifest, and development report. It does not accept a model-quality threshold.

The default --dataset is data/gold/v1.0. --output-dir changes the evaluation artifact root. Diagnostic and inference timeout controls match classify. No credentials, new dependencies, or silent model downloads are involved. Held-out inference requires a compatible --frozen-config plus --allow-held-out and a separate owner decision. See [evaluation](EVALUATION.md) for the artifact lifecycle, exact metrics, and limitations. Audio/UI commands remain unimplemented.
