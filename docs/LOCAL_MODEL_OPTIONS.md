# Local model options

Status: observed setup and planned model candidates, 2026-11-05. Batch 1 diagnostics are implemented; see [local setup](LOCAL_SETUP.md). Local inference is now build scope under [F-004](../features/active/F-004-local-model-pipeline/01_REQUIREMENTS.md). No classifier is selected; no model is downloaded or evaluated.

## Observed laptop and runtime

Read-only hardware and API checks found an ASUS Zenbook UX6404VI, Intel Core i9-13900H, 31.6 GiB RAM, and an NVIDIA RTX 4070 Laptop GPU. The GPU reports 8188 MiB total and 7364 MiB free at this check, with NVIDIA driver 566.07. Free memory changes as applications run.

Ollama 0.40.14 responds at http://127.0.0.1:11434. Its installed-model list is empty. The GPU and driver meet [Ollama's documented NVIDIA requirements](https://docs.ollama.com/gpu). This confirms compatibility, not measured inference speed.

## Recommendation for this laptop

Use Whisper large-v3-turbo as the first speech-to-text candidate, with faster-whisper as the proposed runtime. Keep Whisper small as a lightweight fallback. The [Whisper reference implementation](https://github.com/openai/whisper#available-models-and-languages) lists approximately 6 GB VRAM for turbo and 2 GB for small. Runtime, precision, audio length, and batching affect actual memory.

[Faster-whisper](https://github.com/SYSTRAN/faster-whisper) supports GPU execution and mixed INT8/FP16 computation. Its GPU dependencies include CUDA 12 cuBLAS and cuDNN 9. Those libraries have not been verified or installed for this project. Test one recording with a modest batch size before declaring the setup usable.

Run transcription and classification sequentially, releasing GPU model memory between stages when needed. Two resident models could exhaust the laptop's available VRAM. RAM capacity does not substitute for GPU memory without a speed tradeoff.

The user deferred callback-classifier selection (SRC-015). [Qwen3.5:4b](https://ollama.com/library/qwen3.5:4b) remains a candidate with a roughly 4.0 GB download, not a selected default. Choose classification quality using the development split; freeze the configuration before held-out evaluation.

[Gemma4:e2b](https://ollama.com/library/gemma4:e2b) supports text and audio and is an alternative for a shared Ollama runtime. Its roughly 7.5 GB package is a download size, not a VRAM estimate. Its memory fit and transcription quality have not been tested here, so it is an experiment rather than the initial recommendation. Ollama documents the [audio transcription endpoint](https://docs.ollama.com/api/openai-compatibility).

Cloud models are unnecessary for the first local experiment. If considered later, Ollama cloud requires usage credits or a paid plan. The user handles any sign-in or key creation; no authentication or key action is authorized for the agent.

## Selectable stages

The requested app has separate speech-to-text and callback-classifier choices. Text input skips transcription. Audio becomes an inspectable, editable transcript before classification. Speech synthesis is outside the current scope.

The future selectors show compatible, configured models and identify unavailable models before a run. They do not silently download a model or switch to cloud. A capable multimodal model could be chosen for both stages.

Record each stage's runtime, exact model identifier or revision, relevant settings, and transcript version. Keep transcription quality separate from callback decision quality. Paired fictional recordings and reviewed reference transcripts are still needed to evaluate audio.

These requirements and planned candidates are sequenced in the [implementation plan](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md); the explicit registry and read-only Ollama adapter now exist. UI selectors and the inference pipeline remain planned. D-003 remains open in the [project brief](../intake/PROJECT_BRIEF.md).
