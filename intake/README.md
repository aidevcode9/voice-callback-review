# Project intake sources

No recordings, transcripts, statement of work, or external PRD have been supplied. The initial sources are direct user instructions in this chat.

## Source register

| Source ID | Date and title | Location | Authority |
| --- | --- | --- | --- |
| SRC-018 | 2026-11-06: batch 2 classifier selection | Owner selected qwen3.5:4b-q4_K_M in the model-choice question, which explicitly authorized downloading that model and development-only inference checks | Provision the selected local tag and implement F-004 batch 2. No evaluation, audio, dashboard, cloud, or publication scope added. |
| SRC-016 | 2026-11-05: local inference enters build scope | User requests a workflow plan and PRD update and says this is part of the build now | Include local runtime setup, selectable models, text classification, and transcription in the build plan. Classifier selection remains deferred. |
| SRC-017 | 2026-11-05: next implementation chat | User requests another GPT-6.1 Sol high thread for the next batch | Start a separate chat with those model settings and a bounded implementation handoff. |
| SRC-012 | 2026-11-05: local model development | User reports no OpenAI or Claude key and asks about local runners | Explore local inference without provisioning cloud credentials. |
| SRC-013 | 2026-11-05: Ollama setup instructions | User supplies official documentation and setup sequence | Read docs, inspect hardware, recommend suitable models; do not sign in, create, or use keys for the user. |
| SRC-014 | 2026-11-05: two stages and model choice | User asks about speech-to-text as well as classification and wants to pick | Support independent model choices; speech synthesis is not requested. |
| SRC-015 | 2026-11-05: laptop fit and classifier deferral | User requests the best sensible laptop fit and answers Choose the classifier later | Recommend using observed hardware; leave classifier selection open. |
| SRC-011 | 2026-11-05: candidate labels approved | User explicitly answered approved after clarification that the question covered all 40 proposed labels as-is | Human approval of the unchanged 40-case candidate set; no label corrections supplied. |
| SRC-010 | 2026-11-05: full callback rubric and proceed | User accepts all proposed outcomes, including final resolution, and says to proceed | Callback policy v1.0 accepted; proceed with the rubric and candidate preparation workflow. |
| SRC-009 | 2026-11-05: unresolved issue callback rule | User response to the ambiguous follow-up example | Accepted callback required because the caller states that the issue remains unresolved; no explicit callback request or promise is necessary. |
| SRC-001 | 2026-11-05: voice project idea | User message beginning "So I'm gonna try it out our workflow" | Direct project intent: interview learning, callback assessment, golden set, simple dashboard, and an explainable development workflow. |
| SRC-002 | 2026-11-05: separate project | Follow-up beginning "crfeate it in a new project" | Direct instruction to create a separate repository directory. |
| SRC-003 | 2026-11-05: project location | Follow-up "move it to projects out of skill-building" | Direct instruction to place the repo under the parent projects directory. |
| SRC-007 | 2026-11-05: project orchestration | User clarification about when to create the project orchestrator | Configure the project-specific skill router during intake, before implementation. |
| SRC-008 | 2026-11-05: pstack consideration | User confirmation about future workflow and relevant pstack skills | Compare relevant pstack candidates with house skills to choose the best-fitting method. |
| SRC-005 | 2026-11-05: diagrams | User message requesting architecture and user-flow diagrams | Direct documentation preference for this project. |
| SRC-006 | 2026-11-05: workflow audit | User question about selected skills, orchestration, and following the workflow | Direct request for an explicit record of methods and actual progress. |
| SRC-004 | 2026-11-05: input choice | Answer to the audio-versus-text intake question | Selected audio upload and text transcripts, with callback decisions evaluated on text first. |

The user's interview context mentions Internet Brands and law firms. This records the motivation for a fictional demonstration. It does not establish company ownership, an internal workflow, access to company data, or an endorsed product requirement.

## Material storage

Keep any future raw sources under the ignored `sources/transcripts/`, `sources/sow/`, or `sources/prd-drafts/` directories, or in their approved original location. Record source IDs and relevant sections here. Do not place API keys or real client information in tracked project documents.

## Outputs

See the [brief](PROJECT_BRIEF.md), [working PRD](../docs/PRD.md), and [workflow profile](../.codex/workflow-profile.md). The first backlog proposal defines the callback rubric before dataset labels are treated as authoritative.
