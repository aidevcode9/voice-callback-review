# Explain the planned demo

Status: planned walkthrough. Gold v1.0, the Python classifier/evaluation core and one historical text-v1 development baseline exist. The text workspace is a static simulation; production application and audio remain unimplemented.

## Explain the product

The app reviews a completed service call and recommends whether a representative should call the person back. A reviewer can inspect the transcript and supporting excerpt. An uncertain conversation goes to review.

For audio input, transcription comes before the callback decision. We evaluate the decision on known text first, then compare reference text and transcribed audio to understand where errors enter.

## Explain the workflow

1. Show the intake source register and the decisions the user actually made.
2. Show the PRD and a specific acceptance requirement.
3. Show the selected feature and explain why its document size fits the work.
4. Show the reviewed label rubric and the provenance of the golden examples.
5. Run the relevant checks and inspect an actual failure as well as a correct result.
6. Show the change made in response and the evidence for its result.
7. Explain what remains unverified and which decisions would be needed before broader use.

These steps describe the intended demonstration. Replace proposed steps with recorded evidence as features are implemented.

## Explain what makes it a voice application

The recording is an input with its own error modes. A good explanation distinguishes transcription quality, callback decision quality, and the reviewer's operational decision. The dashboard lets a person follow those stages rather than seeing only a final label.

## Text-first walkthrough

Show a fictional development transcript, select the model and explicitly classify. Read exact evidence, explain the accepted rule, edit into a new version, inspect an earlier result and record a separate human decision. The implemented Review desk supports this flow with local Ollama; saved outputs retain actual provenance. The static design prototypes and labeled controlled browser fixtures are simulations and must be presented as such. Keep held-out cases and answers out of this walkthrough. Show historical evaluation evidence separately, with source/prompt versions and limitations; callback-text-v2 live baseline and candidate freeze remain pending. Audio upload/transcription and paired comparison are the final future stage, after the text workflow is verified.
