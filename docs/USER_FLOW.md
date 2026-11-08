# Reviewer flow

Status: F-006 implements the local production text workspace and verifies its browser/API flow with a controlled Ollama HTTP fixture. SRC-024 defers audio to the [roadmap](ROADMAP.md).

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
```

Changing a selector/filter/case, saving text, inspecting history or recording human review never starts inference. The displayed evidence belongs to the selected run's original transcript, even after a newer edit. A human decision never replaces the model output or modifies gold. Empty, running, timeout, malformed-output and unavailable-runtime states have explicit recovery; processing errors are not needs_review policy outcomes.

Development examples are input-only; the iterative UI excludes held-out cases and answers. Formal evaluation remains separate. The [PRD](PRD.md) owns product intent; [F-006](../features/completed/F-006-text-review-workspace/01_REQUIREMENTS.md) owns browser/API acceptance; [F-004](../features/active/F-004-local-model-pipeline/01_REQUIREMENTS.md) owns core text evaluation.

## Development evaluation review

This is separate from reviewing one service call. The F-011 first slice is a command
and local readable report, rather than an additional app page.

```mermaid
flowchart TD
    Choose[Choose model and optional saved baseline] --> Start[Run evaluate command]
    Start --> Setup[Verify committed source and optional tracing settings]
    Setup --> Progress[Observe saved-case progress]
    Progress --> Complete{Run completed?}
    Complete -- No --> Recover[Inspect preserved partial run; recover runtime if required]
    Complete -- Yes --> Report[Open local browser report]
    Report --> Cases[Inspect unsafe misses, failures and exact case evidence]
    Cases --> Compare[Compare compatible baseline metrics and paired changes]
    Compare --> Next[Explicitly change the next experiment or select candidate]
    Saved[Evaluations command: saved history] --> Report
```

Reviewing a saved report starts no model or tracing request. Expected answers appear
only in completed development reports, after inference. Candidate freezing remains
an explicit command; held-out execution requires its original separate opt-in.
