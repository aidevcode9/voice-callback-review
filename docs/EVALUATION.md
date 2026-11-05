# Proposed evaluation flow

Status: design proposal. No dataset is accepted as gold, and no evaluation has run. The [PRD](PRD.md) owns the rubric, metrics, and acceptance decisions.

```mermaid
flowchart TD
    Candidates["Fictional candidate conversations"] --> Label["Independent human labeling using the rubric"]
    Label --> Dataset["Versioned and reviewed examples"]
    Dataset --> Split["Group related examples and freeze the split"]
    Split --> Dev["Development examples"]
    Split --> Gold["Held-out golden cases"]
    Dev --> Design["Develop prompt and decision behavior"]
    Design --> Freeze["Freeze candidate system version"]
    Freeze --> Run["Run callback evaluator"]
    Gold -->|Transcript inputs only| Run
    Run --> Outputs["Predicted outcome and supporting evidence"]
    Gold -->|Expected labels| Score["Score and inspect disagreements"]
    Outputs --> Score
    Score --> Report["Confusion matrix, counts, review rate, and errors"]
```

The reference answers reach the scorer. They do not reach the callback evaluator. Do not revise a gold label merely because the candidate disagrees; a justified labeling correction creates a new dataset version.

## Add audio after the text baseline

```mermaid
flowchart LR
    Pair["Paired fictional recording and reviewed transcript"] --> Reference["Reference text"]
    Pair --> Audio["Recorded audio"]
    Audio --> STT["Transcription"]
    Reference --> TextRun["Callback evaluation on reference text"]
    STT --> AudioRun["Callback evaluation on transcribed text"]
    Reference --> CompareText["Inspect transcription differences"]
    STT --> CompareText
    TextRun --> CompareDecision["Compare callback decisions and evidence"]
    AudioRun --> CompareDecision
```

Comparing both paths helps distinguish decision errors from transcription-induced errors. An audio failure stays visible as a processing failure. There are no quality or performance results to report at this stage.
