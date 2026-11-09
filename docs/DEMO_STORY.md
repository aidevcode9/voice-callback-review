# Technology leadership demonstration

Use fictional text to show a local callback review workflow and the engineering decisions behind it. Audio upload and voice-to-text are [future enhancements](ROADMAP.md), not part of the current demonstration.

## Walk through the product

1. Open the implemented Review desk and load a fictional development transcript or paste fictional text.
2. Select the available local classifier and explicitly submit it. Explain that choosing a model or editing text does not run inference.
3. Inspect the outcome, policy rules, reason, and exact supporting text. Record a separate human decision.
4. Edit the transcript, save a new version, and inspect the earlier run and its provenance.
5. Show an error or recovery state using the controlled fixture evidence, and explain that a processing failure is not a callback outcome.

For a live classifier demonstration, check the local runtime first. The [browser evidence](evidence/F-006/README.md) uses a controlled Ollama HTTP fixture; it proves the browser/API workflow, not model quality. Static design prototypes are simulations. Do not use held-out cases or answers in the workspace.

## Explain the engineering and limits

Show the source register, accepted callback policy, feature requirements, and frozen human-approved gold set. Run `voice-callback evaluate --model qwen35-4b` from a clean committed checkout, or inspect a saved run with `voice-callback evaluations --run-dir reports/text/RUN_ID`. Open the printed browser report, inspect cases and failures, and compare a compatible saved baseline with `--baseline reports/text/BASELINE_ID`. The [evaluation guide](EVALUATION.md) explains input/answer separation, immutable artifacts, and comparison limits.

The current-source callback-text-v2 development baseline matched 20/20 fictional labels; SRC-026 accepts F-004 text delivery after owner testing and QA. This result does not establish production quality or held-out performance. Actual candidate freeze, real held-out inference, numeric production targets, hosting, and audio remain [follow-up work](ROADMAP.md). Present implementation, development evidence, owner acceptance, and deployment as separate facts.
