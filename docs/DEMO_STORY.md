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

Show the source register, accepted callback policy, feature requirements, and frozen human-approved gold set. Explain that evaluation separates inputs from expected answers and preserves processing failures in its metrics. The historical callback-text-v1 development run matched 20 of 20 fictional development labels once; it does not establish repeatability, production quality, or held-out performance.

The fresh callback-text-v2 development baseline, candidate freeze, numeric quality thresholds, and broader product acceptance remain open. Held-out inference requires a matching freeze and separate owner authorization. Hosting and deployment remain separate decisions. Present hardening as ongoing work and point to verified changes rather than claiming the system is production-ready.
