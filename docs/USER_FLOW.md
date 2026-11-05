# Proposed user flow

Status: product proposal. No screen or interaction has been implemented.

```mermaid
flowchart TD
    Start["Open the review dashboard"] --> Input{"Choose an input"}
    Input -->|Text| Text["Paste or upload a transcript"]
    Input -->|Audio| Audio["Upload a recorded call"]
    Audio --> Transcribe["Create a transcript"]
    Transcribe -->|Failure| Error["Show the transcription error"]
    Error --> Audio
    Transcribe -->|Success| Inspect["Inspect the transcript"]
    Text --> Inspect
    Inspect --> Correct{"Correct the text?"}
    Correct -->|Yes| Version["Save a new transcript version"]
    Correct -->|No| Analyze["Request a callback recommendation"]
    Version --> Analyze
    Analyze -->|Failure| DecisionError["Show a decision error"]
    DecisionError --> Analyze
    Analyze -->|Success| Result["Show outcome, reason, and evidence"]
    Result --> Review{"Reviewer agrees?"}
    Review -->|Yes| Keep["Keep the model recommendation"]
    Review -->|No| Override["Record a separate reviewer decision"]
    Keep --> List["Return to the case list"]
    Override --> List
```

The outcome can be callback required, no callback required, or needs review. Transcription and decision failures are processing errors, not no-callback results. A reviewer decision does not silently change the expected label of a golden case.

The [PRD](PRD.md) owns the behavior and acceptance requirements. [Architecture](ARCHITECTURE.md) shows the proposed logical components.
