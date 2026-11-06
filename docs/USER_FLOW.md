# Proposed user flow

Status: product proposal. No screen or interaction has been implemented.

```mermaid
flowchart TD
    Start["Open the review dashboard"] --> Input{"Choose an input"}
    Input -->|Text| Text["Paste or upload a transcript"]
    Input -->|Audio| Audio["Upload a recorded call"]
    Audio --> STTChoice["Choose an available speech-to-text model"]
    STTChoice --> Transcribe["Create a transcript"]
    Transcribe -->|Failure| Error["Show the transcription error"]
    Error --> Audio
    Transcribe -->|Success| Inspect["Inspect the transcript"]
    Text --> Inspect
    Inspect --> Correct{"Correct the text?"}
    Correct -->|Yes| Version["Save a new transcript version"]
    Correct -->|No| ClassifierChoice["Choose an available callback model"]
    Version --> ClassifierChoice
    ClassifierChoice --> Analyze["Request a callback recommendation"]
    Analyze -->|Failure| DecisionError["Show a decision error"]
    DecisionError --> Analyze
    Analyze -->|Success| Result["Show outcome, reason, and evidence"]
    Result --> Review{"Reviewer agrees?"}
    Review -->|Yes| Keep["Keep the model recommendation"]
    Review -->|No| Override["Record a separate reviewer decision"]
    Keep --> List["Return to the case list"]
    Override --> List
```

The model choices are independent; a compatible multimodal model may serve both stages. Unavailable choices are reported before execution. Text input does not require a speech-to-text model. Each run records both the transcript version and the model configuration used.

The outcome can be callback required, no callback required, or needs review. Transcription and decision failures are processing errors, not no-callback results. A reviewer decision does not silently change the expected label of a golden case.

The [PRD](PRD.md) owns the behavior and acceptance requirements. [Architecture](ARCHITECTURE.md) shows the proposed logical components.
