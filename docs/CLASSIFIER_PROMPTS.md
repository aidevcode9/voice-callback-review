# Classifier prompt ownership and versions

The current classifier instructions live in [callback-text-v2.txt](../src/voice_callback/prompts/callback-text-v2.txt). The API, CLI and evaluation runner share the request builder in src/voice_callback/classify.py; the UI does not keep a second prompt.

PROMPT_VERSION in classify.py is the authoritative selector. The builder loads the matching prompts/PROMPT_VERSION.txt package resource, appends the accepted [callback policy](CALLBACK_POLICY.md), then appends the JSON response schema generated from Python contracts. The transcript remains a separate user message containing JSON data. Keep policy and schema ownership separate from the instruction file.

The file contains the instruction prefix only. Its spaces and final two LF newlines are intentional. The extraction preserves the exact callback-text-v2 system message and request, so the prompt version stays v2. Tests pin the pre-extraction rendered prompt hash and a fixed synthetic request hash. No trim, dedent, line-ending conversion, placeholder substitution or second schema copy is applied at load time.

The v2 file has a specific .gitattributes exception for blank-at-EOF checks because those separator bytes are part of the prompt. Other whitespace checks remain enabled. Do not remove the final blank line as a cosmetic cleanup.

## Changing instructions

1. Create a new versioned prompt file, preserving prior versions in Git history. Change PROMPT_VERSION to select the new version. Do not silently change v2's meaning while continuing to label it v2.
2. Review the fully assembled system message, including policy and schema. A policy or schema change can also change the rendered prompt hash even when the instruction prefix is unchanged; treat that as a prompt-contract change and review its version/evaluation implications.
3. Update compatibility expectations deliberately. Run the classifier/evaluation tests, package smoke check and configured snapshot gates. The installed-wheel check constructs a request from the actual packaged resource without importing repository source.
4. Commit the implementation before a fresh development evaluation. Inspect the new baseline before any explicit candidate freeze. Existing frozen runs remain tied to their original source revision, configuration and artifacts. Held-out execution remains a separate owner decision.

The package includes prompts/*.txt through setuptools package data. Evaluation source identity hashes those assets using relative paths alongside package Python files. Every run also records the selected prompt version, the exact assembled system-message hash and the complete request hash. Moving content into a file changes source/code identity even when the rendered prompt hash stays the same, so it does not preserve compatibility with a previous frozen code revision.

## Verification record

[F-007](../features/completed/F-007-versioned-classifier-prompt/FEATURE.md) records the extraction baseline, acceptance criteria and observed checks. No live inference, model quality result, new freeze or stored review migration is part of this refactor. Restart an already running backend to load the updated Python request builder; restarting does not submit inference or change saved history.
