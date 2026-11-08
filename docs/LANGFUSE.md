# Langfuse tracing

Tracing is optional and disabled unless `VCR_LANGFUSE_ENABLED=1`. It sends operational metadata to the Langfuse endpoint in `LANGFUSE_BASE_URL`; inference remains local. A classifier run contains a `callback-classification` span and, when inference starts, an `ollama-classification` generation. They contain the run ID, configured model, success/failure status, timing, and Ollama token counts when supplied. Transcripts, prompts, case identifiers, evidence, outputs and raw errors are not sent. Evaluation runs deliberately bypass tracing to preserve dataset isolation. No customer data is required to verify this integration.

Langfuse Python SDK 5.2.0 requires Python 3.11 or newer and Langfuse Cloud or a compatible v4 server. The application without tracing continues to support Python 3.10. Install the optional hash-locked dependencies into a compatible environment after the standard setup:

```powershell
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-langfuse.txt
```

Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_BASE_URL` in the environment before starting the app; then set `VCR_LANGFUSE_ENABLED=1`. For the local `langfuse.txt` supplied by the owner, the following imports only those three fields into the current PowerShell process without printing values or executing the file:

```powershell
Get-Content .github/workflows/langfuse.txt | ForEach-Object {
    $parts = $_ -split '=', 2
    if ($parts.Count -eq 2) {
        $name = $parts[0].Trim() -replace '^export\s+', ''
        if ($name -in @('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_BASE_URL')) {
            $value = $parts[1].Trim().Trim('"').Trim("'")
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}
$env:VCR_LANGFUSE_ENABLED = '1'
.venv\Scripts\python.exe scripts/run_review_desk.py
```

Run the CLI from the same configured shell to trace CLI classification. Stop tracing by removing the enable variable or setting it to `0` before starting the process. The credentials file is ignored by Git; keep it private. If configuration is incomplete or the SDK cannot initialize, a generic warning is logged and classification continues. Delivery failures can be reported by the SDK; a local classification success does not prove that a remote trace was stored.

Token counts are usage measures, not the total cost of running a local model. Use the [TCO worksheet](../outputs/f009/tco.xlsx) for hardware, electricity, labor and other costs. Do not assign an API token price to local inference without an explicit cost model.
