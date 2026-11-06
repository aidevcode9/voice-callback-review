# Set up local runtime diagnostics

Run these commands in the voice-callback-review repository. Python 3.10 or later is required. Batch 1 was verified with Python 3.13.1 and pip 24.3.1 on Windows.

## Create the project environment

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --disable-pip-version-check --no-deps -e .
.venv\Scripts\python.exe -m pip check
```

The editable install uses the pinned setuptools 80.9.0 build backend in pyproject.toml. Pip may fetch that build dependency from the package index. The application has no third-party runtime dependencies. The virtual environment and generated package metadata are ignored by Git. Activation is optional when commands use the environment's interpreter explicitly.

Audio and dashboard dependencies are deferred to their implementation batches. Neither faster-whisper nor model weights are installed by this setup. No provider SDK, API key, or sign-in is required.

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

The registry is [config/models.json](../config/models.json). Its entries declare capabilities and settings, not installation or a selected default. The shipped entries are large-v3-turbo and small through faster-whisper, both unavailable until later provisioning. Classifier selection remains the owner's D-003 decision.

## Diagnose an unavailable choice

Read installed_models separately from configured_models. A model discovered in Ollama is never automatically added to the registry or chosen as a classifier. Ollama identity matching uses the exact configured tag, including its explicit version tag where supplied. Its observed digest is retained.

Configured entries report not_installed when the server's inventory lacks that model. They report installation_unknown when inventory retrieval fails. Faster-whisper entries report runtime_not_verified because batch 1 does not inspect or provision that runtime. Ollama-only transcription reports adapter_not_implemented. Known remote models report remote_not_supported.

The selectable field identifies a configured, stage-compatible local Ollama inventory match. It does not establish semantic suitability, successful inference, or an implemented classification command. The CLI always reports inference_verified as false in batch 1. A classifier implementation must verify model details and local execution before inference in batch 2.

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

The behavior tests use controlled loopback HTTP servers and a controlled connection-refusal fixture. They need no running Ollama, downloaded models, or external network. Classification, transcription, evaluation, and UI execution remain planned in [F-004](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md).
