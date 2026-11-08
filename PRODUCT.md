# Voice Callback Review product context

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Owner-approved direction: Next.js frontend, thin FastAPI boundary over the existing Python classifier/evaluation core, Nginx routing pages/assets and /api under one browser origin. The FastAPI/SQLite backend foundation is implemented; Next.js and Nginx remain pending. Static HTML/CSS/JavaScript serves this design exploration only. Hosting is undecided; deployment is outside scope.

## Users

The project owner reviews fictional service-call transcripts and demonstrates the engineering work to senior engineers. A service reviewer is a proposed persona, not a validated customer.

## Product Purpose

Make a callback recommendation inspectable through the transcript, exact supporting quotes, accepted policy rules, reason, and preserved run provenance. A human records a separate review decision.

## Operating Context

Local-first, one inference job at a time on the existing laptop. Text entry and fictional development cases come before audio integration. The classifier is explicitly selected; changing controls never invokes inference. Transcription and paired-audio verification are the final stage.

## Capabilities and Constraints

The existing Python CLI provides diagnostics, classification, evaluation, scoring, and freeze preparation. The implemented backend supports versioned transcript edits, explicit submissions, preserved history, separate review decisions and case filters; its production browser workspace remains pending. Runtime failures are distinct from policy outcomes. Missing models never download automatically. Held-out cases and answers stay out of the iterative workspace. Frozen policy, candidates, approval, and gold are immutable.

## Evidence on Hand

[PRD](docs/PRD.md), [accepted policy](docs/CALLBACK_POLICY.md), and [F-004 evidence](features/active/F-004-local-model-pipeline/03_IMPLEMENTATION_PLAN.md) own the detailed record. The historical callback-text-v1 baseline matched 20/20 fictional development labels once. callback-text-v2 live baseline, candidate freeze, numeric quality acceptance, audio, and application acceptance remain pending. PR #1 and PR #2 are merged; this branch includes origin/main c82f0ed. Prototype outputs are simulations, not model measurements.

## Product Principles

- Read the evidence before accepting the recommendation.
- Preserve model output, human judgment, and gold as separate records.
- Make each inference an explicit, traceable action.
- Keep failures and uncertainty visible without inventing outcomes.

## Open Decisions

The owner selected A Review desk on 2026-11-06 and authorized implementation (SRC-021). B Casebook remains historical comparison evidence. Hosting and numeric quality thresholds remain open. Specific API limits and persistence design are proposals in F-006, not accepted operating guarantees.
