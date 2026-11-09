# Voice Callback Review product context

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

The local Review desk uses Next.js, a FastAPI/SQLite boundary over the Python classifier/evaluation core, and Nginx routing pages and /api under one browser origin. Static HTML/CSS/JavaScript prototypes are historical simulations. Hosting is undecided; deployment is outside scope.

## Users

The project owner reviews fictional service-call transcripts and demonstrates the engineering work to senior engineers. A service reviewer is a proposed persona, not a validated customer.

## Product Purpose

Make a callback recommendation inspectable through the transcript, exact supporting quotes, accepted policy rules, reason, and preserved run provenance. A human records a separate review decision.

## Operating Context

Local-first, one inference job at a time on the existing laptop. The current workflow uses text entry and fictional development cases. The classifier is explicitly selected; changing controls never invokes inference. Audio and transcription are deferred to the [roadmap](docs/ROADMAP.md).

## Capabilities and Constraints

The existing Python CLI provides diagnostics, classification, evaluation, scoring, and freeze preparation. The implemented browser workspace and backend support versioned transcript edits, explicit submissions, preserved history, separate review decisions and case filters. Runtime failures are distinct from policy outcomes. Missing models never download automatically. Held-out cases and answers stay out of the iterative workspace. Frozen policy, candidates, approval, and gold are immutable.

## Evidence on Hand

[PRD](docs/PRD.md), [accepted policy](docs/CALLBACK_POLICY.md), and [F-004 evidence](features/completed/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) own the detailed record. The current-source callback-text-v2 development baseline matched 20/20 fictional labels. SRC-026 accepts F-004 text delivery after owner testing and QA. Candidate freeze, real held-out measurement, and numeric production-quality targets remain follow-up work. Prototype outputs are simulations, not model measurements.

## Product Principles

- Read the evidence before accepting the recommendation.
- Preserve model output, human judgment, and gold as separate records.
- Make each inference an explicit, traceable action.
- Keep failures and uncertainty visible without inventing outcomes.

## Open Decisions

The owner selected A Review desk on 2026-11-06 and authorized implementation (SRC-021). B Casebook remains historical comparison evidence. Hosting and numeric quality thresholds remain open. F-006 implements API limits and persistence; controlled browser evidence verifies the local workflow, not production operating guarantees.
