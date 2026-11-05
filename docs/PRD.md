# Voice Callback Review: product requirements

Status: draft for discussion.
Product and acceptance owner: the user.
Sources: SRC-001 and SRC-004 in the [source register](../intake/README.md).
Last updated: 2026-11-05.
Acceptance record: input modes selected; the remaining product design is proposed.

## Purpose

Build a small post-call review application that recommends whether a service representative should call someone back. Use it to learn about voice application design and demonstrate a repository-based development process.

The interview context motivates a fictional law-firm service example. No company-specific operating policy has been supplied.

## Users and outcome

A reviewer can inspect a call, understand the callback recommendation, see the evidence behind it, and correct a mistake. The project owner can demonstrate how the system was specified and evaluated.

The core question is operational: does this conversation leave a callback action for a service representative? It does not assess legal merit or give legal advice.

## Confirmed input choice

The demo accepts uploaded prerecorded audio and existing text transcripts. Callback decision evaluation starts with text. Transcription is assessed separately before evaluating the combined audio-to-decision flow. This choice was made by the user in SRC-004.

## Proposed first-demo scope

1. Supply a text transcript or upload a prerecorded call.
2. For audio, create a transcript and display transcription success or failure separately from decision status.
3. Retain the original transcript and identify any reviewer correction used for a new decision.
4. Recommend one of three outcomes and provide a short reason plus a supporting excerpt.
5. Display cases and their current recommendations in a small dashboard.
6. Compare model recommendations against a versioned golden set and inspect errors.

The initial interface needs a case list, filters for the recommendation, a case detail view, and an evaluation summary. A numeric confidence percentage is not required. The first design should favor evidence the reviewer can inspect.

The proposed [user flow](USER_FLOW.md), [architecture](ARCHITECTURE.md), and [evaluation flow](EVALUATION.md) show how these responsibilities connect.

## Proposed callback rubric

| Outcome | Working definition | Fictional example |
| --- | --- | --- |
| Callback required | The caller explicitly requests a return call, the representative promises one, or an unresolved service request explicitly needs later contact. | "Please have someone call me back about scheduling my consultation." |
| No callback required | The conversation establishes that the request is resolved and no follow-up is outstanding, or it is clearly a non-actionable wrong-number or spam call. | "That answers my question. I don't need anything else." |
| Needs review | The transcript is incomplete, contradictory, unintelligible, or lacks enough context to decide whether follow-up remains. | A recording ends before the representative answers the request. |

This rubric is a proposal, not a supplied firm policy. Missing contact details do not by themselves mean no callback is needed. A recommendation does not prove that a callback has occurred. Urgency scoring and service-level deadlines are outside the first rubric.

## Product requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| PRD-R001 | Accept text transcripts and prerecorded audio. | Both entry paths produce an inspectable case; invalid or unsupported input displays a useful error. |
| PRD-R002 | Keep transcription and callback decisions distinguishable. | An audio failure cannot appear as a successful no-callback decision; original and corrected transcript versions remain identifiable. |
| PRD-R003 | Apply the agreed callback rubric with an explicit needs-review option. | Representative labeled examples cover all outcomes, contradictory requests, and incomplete calls. |
| PRD-R004 | Show the reason and supporting transcript excerpt. | The excerpt exists in the transcript version used for the decision; unsupported claims are visible as failures. |
| PRD-R005 | Let a person inspect and correct a recommendation. | The dashboard distinguishes the original model output from the reviewer decision. It does not automatically relabel gold data. |
| PRD-R006 | Maintain an independently reviewed golden set. | Each accepted case has a stable ID, transcript, expected outcome, rationale, provenance, reviewer, and dataset version. |
| PRD-R007 | Evaluate a frozen system against held-out cases without label leakage. | A reproducible run identifies dataset, prompt, model, and input versions and reports counts and errors. |
| PRD-R008 | Make the development and demo process explainable. | The owner can walk through intake, requirements, a feature plan, golden labels, observed errors, and an iteration without claiming unrun results. |

## Golden set and evaluation

Start with a proposed small candidate collection of roughly 30 to 50 fictional transcripts. Include clear positives, clear negatives, ambiguous cases, truncated conversations, explicit callback promises, already-resolved requests, and wording variations. The count and composition await D-002.

A person reviews candidate labels using the rubric before the collection is called gold. Candidate model outputs cannot define their own expected answers. Keep development examples separate from held-out evaluation cases, and keep related conversations or paraphrases in the same split.

Report a three-outcome confusion matrix, strict callback recall, callback precision, needs-review rate, and concrete mistakes. Strict recall counts a needs-review output as not automatically detecting a required callback. Also report unsafe misses where a gold callback-required case is predicted no callback. Show small-sample counts beside percentages.

Do not silently discard needs-review cases or change expected labels to improve a run. Changes to labels create a new dataset version with a recorded reason. Model choice and numeric quality thresholds remain open until a baseline exists and the acceptance owner selects them.

For the audio extension, use paired recordings and reviewed reference transcripts. Compare decisions from reference text with decisions from transcribed audio. This separates transcription errors from decision errors. No transcription or callback quality results exist yet.

## Exclusions

Live phone handling, speaking agents, automatic dialing, CRM writes, legal guidance, case qualification, production authentication, and production multi-firm deployment are outside the proposed first demo. No real customer recordings are needed for the learning prototype.

## Proposed acceptance flow

A reviewer supplies a text example, inspects a recommendation and excerpt, compares it to its expected label, and corrects an error. The reviewer then uploads a short fictional recording and can trace the transcript version used for its recommendation. An evaluation run produces an inspectable report, including failures and review cases.

Functional implementation, decision quality, and audio quality are separate acceptance areas. No product-quality threshold or acceptance result is approved by this draft.

Open decisions and owners are tracked in the [project brief](../intake/PROJECT_BRIEF.md). The next step is [F-001: callback rubric](../features/backlog/F-001-callback-rubric/FEATURE.md).
