# Local model options

Status: classifier selected and provisioned, 2026-11-06. The owner chose qwen3.5:4b-q4_K_M for [F-004 batch 2](../features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md). Focused development inference works through the [local setup](LOCAL_SETUP.md). Formal model evaluation remains batch 3.

## Observed laptop and runtime

Read-only hardware and API checks found an ASUS Zenbook UX6404VI, Intel Core i9-13900H, 31.6 GiB RAM, and an NVIDIA RTX 4070 Laptop GPU. The GPU reports 8188 MiB total and 7364 MiB free at this check, with NVIDIA driver 566.07. Free memory changes as applications run.

The 2026-11-05 check found Ollama 0.40.14 and zero models. On 2026-11-06, read-only diagnostics found 0.40.15 and zero models before provisioning. The selected model is now installed. The GPU recheck reported 8188 MiB total and 7596 MiB free before inference, with the same driver. The GPU meets [Ollama's documented NVIDIA requirements](https://docs.ollama.com/gpu). Restricted-shell loopback failed; broader socket access verified the actual server.

## Historical transcription candidates for this laptop

SRC-024 defers audio and transcription to the [roadmap](ROADMAP.md). The following earlier recommendations are unverified options, not a selected implementation or current delivery commitment.

Use Whisper large-v3-turbo as the first speech-to-text candidate, with faster-whisper as the proposed runtime. Keep Whisper small as a lightweight fallback. The [Whisper reference implementation](https://github.com/openai/whisper#available-models-and-languages) lists approximately 6 GB VRAM for turbo and 2 GB for small. Runtime, precision, audio length, and batching affect actual memory.

[Faster-whisper](https://github.com/SYSTRAN/faster-whisper) supports GPU execution and mixed INT8/FP16 computation. Its GPU dependencies include CUDA 12 cuBLAS and cuDNN 9. Those libraries have not been verified or installed for this project. Test one recording with a modest batch size before declaring the setup usable.

Run transcription and classification sequentially, releasing GPU model memory between stages when needed. Two resident models could exhaust the laptop's available VRAM. RAM capacity does not substitute for GPU memory without a speed tradeoff.

## Classifier comparison and owner selection

Official tags and publisher cards were checked on 2026-11-06. Sizes below are rounded package sizes in decimal GB, not VRAM requirements. Context maxima describe model capability, not a recommended laptop allocation.

| Exact local Ollama tag | Package and maximum context | Fit and callback reasoning assessment |
| --- | --- | --- |
| [qwen3.5:4b-q4_K_M](https://ollama.com/library/qwen3.5:4b-q4_K_M) | 3.3 GB, Q4_K_M, 256K | Recommended first candidate, then selected by the owner. A compact model with configurable reasoning; plausible room for modest context on 8 GiB VRAM. Actual residency and callback accuracy require checks. |
| [qwen3:4b-instruct-2507-q4_K_M](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M) | 2.5 GB, Q4_K_M, 256K | Lighter text-only alternative. Its non-thinking instruction model offers a simpler response path and more memory margin. No claim that it is less accurate on this task. |
| [gemma4:e2b-it-q4_K_M](https://ollama.com/library/gemma4:e2b-it-q4_K_M) | 4.6 GB, Q4_K_M, 128K | Plausible local alternative with less memory margin. Multimodal capabilities do not establish better text classification or transcription. No local run performed. |

The earlier qwen3.5:4b and gemma4:e2b names are valid family tags. Their current tag indexes list platform-dependent packages of 3.3–4.0 GB and 4.6–7.5 GB respectively. The prior 4.0 and 7.5 GB figures were insufficiently specific for this Windows NVIDIA laptop. Explicit GGUF quantization tags avoid selecting an MLX variant. See the [Qwen3.5 tags](https://ollama.com/library/qwen3.5/tags) and [Gemma 4 tags](https://ollama.com/library/gemma4/tags). Tags remain mutable; runtime digests establish the actual installed identity.

[Qwen3.5's publisher card](https://huggingface.co/Qwen/Qwen3.5-4B) documents text input and thinking controls. Non-thinking mode is a reasonable initial development choice for short policy decisions. Its general benchmarks do not measure our callback policy. The card's large-context reasoning guidance is not evidence that this laptop should allocate 128K or 256K context. The [Qwen3 Instruct 2507 card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) explicitly describes a non-thinking model. Do not substitute qwen3:4b, which currently resolves to the thinking variant.

[Google's Gemma 4 card](https://huggingface.co/google/gemma-4-E2B-it) explains that E2B means effective parameters, with larger embedding tables, and lists text, image, and audio capability. It does not mean a two-billion-weight memory footprint. Audio remains unverified and deferred.

Ollama supports [JSON-schema constrained output](https://docs.ollama.com/capabilities/structured-outputs). That makes all three plausible structured-decision candidates, subject to live integration. Schema compliance cannot establish the right policy outcome or faithful reasoning. The application separately validates labels, rule IDs and their outcome, bounded reasons, and verbatim transcript evidence. Final resolution, surviving promises or requests, ambiguity, and instruction-like transcript text need development checks.

Runtime memory includes weights, context cache, compute buffers, and any encoders. More context increases memory use; system RAM offloading may trade speed for capacity. Start with one classifier at 8192 tokens and release it after each request. No peak VRAM, full-GPU residency, latency target, or comparative quality measurement is claimed. [Ollama context guidance](https://docs.ollama.com/context-length) explains allocation and processor inspection.

The owner also asked about Nemotron 3.5 Super. Local Ollama support exists, but [nemotron-3.5-super:120b-a12b-q4_K_M](https://ollama.com/library/nemotron-3.5-super/tags) lists about 90 GB. [NVIDIA's quantized model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4) describes 120B total and 12B active parameters and much larger deployment hardware. Active parameters reduce per-token computation; they do not make all weights fit this laptop. It was excluded from provisioning.

SRC-018 records the owner's explicit Qwen selection after the comparison, authorizing its download and development-only inference. Installed identity is d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04, with 3,324,173,934 package bytes. Local metadata reports GGUF, Q4_K_M, qwen35, completion, and thinking controls. Batch 2 records the focused results; batch 3 owns scoring and configuration freeze before held-out evaluation. No other classifier, cloud inference, credentials, or audio dependencies were provisioned.

## Selectable stages

The current app offers an explicit callback-classifier choice for text. Independent speech-to-text selection and inspectable transcripts from audio are deferred roadmap ideas. Speech synthesis is outside the current scope.

The future selectors show compatible, configured models and identify unavailable models before a run. They do not silently download a model or switch to cloud. A capable multimodal model could be chosen for both stages.

Record each stage's runtime, exact model identifier or revision, relevant settings, and transcript version. Keep transcription quality separate from callback decision quality. Paired fictional recordings and reviewed reference transcripts are still needed to evaluate audio.

The registry, diagnostics, text classifier, and text UI selector exist. Audio and transcription have no current delivery commitment. D-003's classifier choice is resolved in the [project brief](../intake/PROJECT_BRIEF.md).
