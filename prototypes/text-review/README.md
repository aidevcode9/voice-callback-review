# Text review design prototypes

Open [the comparison](index.html), [A Review desk](desk.html) or [B Casebook](casebook.html) directly in a browser. No install, model, API, audio dependency or production stack is required. The shared CSS/JavaScript keeps both directions on the same fictional workflow. Newly authored DEMO-101 through DEMO-103 are independent simulation fixtures; no frozen input/answer file is loaded.

All recommendations, states, model settings and processing in these artifacts are illustrative. Browser storage preserves each direction's sample versions/runs/reviews independently under vcr-prototype keys. It is not production persistence. Reset clears only the selected direction's sample state. The actual API's proposed durable storage, job admission, idempotency and recovery are specified in [F-006](../../features/completed/F-006-text-review-workspace/02_TECHNICAL_SPEC.md).

## Review the directions

| Direction | Structural choice | Strength | Tradeoff |
| --- | --- | --- | --- |
| A Review desk | Persistent case rail, transcript and decision columns, history below | Repeated testing and evidence/decision comparison with less scrolling | More dense at desktop widths; stacks at narrow widths |
| B Casebook | Horizontal case navigation, decision/review band, full-width conversation | Guided walkthrough and long-form reading | More vertical travel between evidence, history and decisions |

Recommend A for the owner's engineering review/testing scene. B remains a fully rendered alternative. Neither visual direction is owner-selected yet. Production implementation stops pending that choice.

## Interaction coverage

Paste transcript creates an empty editor; explicit save creates a version. Load fictional case navigates to a sample without inference. Classify is the only simulated submission. A new run retains exact submitted text, version, model and outcome/failure. Run history selects its original transcript/highlight. The selector shows the one configured Qwen classifier; no alternative model is invented. Filter/case/selector interactions do not submit. Human decisions append separately; they do not replace output. Prototype settings simulate valid, loading, timeout, malformed and unavailable-runtime states; they do not configure Ollama.

Edited/pasted text receives an explicitly illustrative needs-review response; this is not a semantic classifier. No actual model digest/hash or inference timing is invented. Prototype availability restoration is simulated. Full production contract/admission/restart behavior, multi-quote evidence and shared CLI contention remain future checks.

## Reproduce browser verification

The check script uses an already installed Playwright package and Chromium. It does not install dependencies. Set PLAYWRIGHT_MODULE to the existing package directory and optionally CHROMIUM_EXECUTABLE to an existing browser executable, then run node prototypes/text-review/verify.cjs. It drives the actual static artifacts, writes evidence to screenshots/ and verification.json, and resets the isolated test browser context between scenarios. No model or external request is made.

## Evidence

Desktop captures are 1440 × 1000; narrow captures are 390 × 844, full document from the top. State captures include empty, loading, timeout, malformed output, runtime unavailable, editing and provenance. See [verification results](verification.json). Rendered captures and independent finish review are recorded in the F-006 plan. Captures are browser output from these local sources, not generated artwork.

Prototype acceptance supports F-006-AC01 only. Production browser/API acceptance AC02–AC10 is pending implementation. Python core tests and live model evaluation are not rerun for this design-only task.

Independent [finish review](REVIEW.md): ship at prototype scope for owner comparison after all listed corrections were scored resolved.

## Local preview

A loopback-only static preview was verified at http://127.0.0.1:8765/index.html. If it is no longer running, use .venv/Scripts/python.exe -m http.server 8765 --bind 127.0.0.1 --directory prototypes/text-review from the repository root, or open index.html directly. This is a static design preview, not the proposed production Nginx/API stack. screenshots/comparison.png captures that comparison page; the other 18 captures cover both directions and states.

Generated screenshot PNGs stay local and are ignored by Git. The verification script recreates them; the comparison page links directly to both runnable prototypes.
