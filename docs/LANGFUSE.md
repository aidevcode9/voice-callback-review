# Langfuse tracing

Tracing is disabled unless `VCR_LANGFUSE_ENABLED=1`. When enabled, it sends the submitted transcript and the validated classifier decision (label, rules, reason, and evidence) to the Langfuse endpoint in `LANGFUSE_BASE_URL`, along with run ID, model, status, timing and available token counts. This can include sensitive call content. Set `VCR_LANGFUSE_CONTENT=0` before starting the app to send operational metadata only. Inference remains local; the system prompt, raw model responses, raw errors and credentials are not included in trace data.

Evaluation emits one trace per case under the same settings. Each trace includes the evaluation ID, dataset version, split, and case ID as metadata so cases can be matched to the local report. Expected labels, reference rationales, and scores stay in local evaluation artifacts; they are not sent to Langfuse. The held-out split retains its separate freeze and authorization requirements. If an authorized held-out evaluation runs with content tracing enabled, its inputs and model decisions will be sent to Langfuse.

For development evaluation, use `.venv\Scripts\python.exe -m voice_callback.cli evaluate --model qwen35-4b --trace`. The [evaluation workflow](EVALUATION.md#run-development-inference-before-scoring) loads root `.env` automatically and keeps tracing optional.

Langfuse Python SDK 5.2.0 requires Python 3.11 or newer and Langfuse Cloud or a compatible v4 server. The application without tracing continues to support Python 3.10. Install the optional hash-locked dependencies into a compatible environment after the standard setup:

```powershell
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-langfuse.txt
```

Copy [.env.example](../.env.example) to root `.env` and fill its three Langfuse fields locally, or set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_BASE_URL` in the process environment. `.env` is ignored by Git; `.env.example` contains placeholders only. Evaluation recognizes only these keys plus `VCR_LANGFUSE_ENABLED`, `VCR_LANGFUSE_CONTENT` and `LANGFUSE_TRACING_ENABLED`. Process values, even empty ones, override file values. Explicit `--trace`/`--no-trace` overrides the application tracing switch.

The bounded literal `.env` format accepts UTF-8/BOM, blank/comment lines, optional `export`, KEY=value, matching single/double quotes and trailing comments. It does not expand variables, interpret escapes or execute shell commands. Diagnostics identify supported keys and line numbers without echoing values. The old TXT file is no longer read by the runtime.

Automatic `.env` loading belongs to the evaluation workflow. For the review desk or standalone `classify`, supply process environment values and set `VCR_LANGFUSE_ENABLED=1` in that process. The example file leaves tracing disabled by default.

Run the CLI from the same configured shell to trace CLI classification. To exclude transcript and decision content, set `$env:VCR_LANGFUSE_CONTENT = '0'` in that shell before starting the application. Stop tracing by removing the enable variable or setting it to `0` before starting the process. The `.env` credentials file is ignored by Git; keep it private. If configuration is incomplete or the SDK cannot initialize, a generic warning is logged and classification continues. Delivery failures can be reported by the SDK; a local classification success does not prove that a remote trace was stored.

Token counts are usage measures, not the total cost of running a local model. Use the [TCO worksheet](../outputs/f009/tco.xlsx) for hardware, electricity, labor and other costs. Do not assign an API token price to local inference without an explicit cost model.
