# Reviewer flow

Status: F-006 implements the local production text workspace and verifies its browser/API flow with a controlled Ollama HTTP fixture. Final audio remains proposed. SRC-020 supersedes audio-first screen planning.

```mermaid
flowchart TD
    Start["Open text review workspace"] --> Input["Paste transcript or explicitly load fictional development input"]
    Input --> Save["Save immutable transcript version"]
    Save --> Select["Choose available classifier"]
    Select --> Submit["Explicitly submit classification"]
    Submit --> Job["One active job; poll and reconnect without resubmitting"]
    Job -->|Failure| Error["Show typed processing failure, no policy outcome"]
    Error --> Retry["Explicit retry only; retain earlier history"]
    Retry --> Submit
    Job -->|Success| Read["Read recommendation, policy rule, reason and exact highlights"]
    Read --> Review["Append separate human decision for this run"]
    Read --> Edit["Edit text and save a new version"]
    Edit --> Select
    Read --> History["Inspect previous run with its original transcript and provenance"]
    Review --> History
    Final["Final stage after text acceptance: upload fictional audio and explicitly transcribe"] -.-> Save
```

Changing a selector/filter/case, saving text, inspecting history or recording human review never starts inference. The displayed evidence belongs to the selected run's original transcript, even after a newer edit. A human decision never replaces the model output or modifies gold. Empty, running, timeout, malformed-output and unavailable-runtime states have explicit recovery; processing errors are not needs_review policy outcomes.

Development examples are input-only; the iterative UI excludes held-out cases and answers. Formal evaluation remains separate. Final audio integration retains independent transcription/classification choices and never classifies failed transcription. The [PRD](PRD.md) owns product intent; [F-006](../features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) owns browser/API acceptance; [F-004](../features/active/F-004-local-model-pipeline/01_REQUIREMENTS.md) owns core evaluation and final audio acceptance.
