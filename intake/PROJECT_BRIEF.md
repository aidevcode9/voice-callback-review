# Project brief

Project: Voice Callback Review.
Intake status: draft, sufficient for product discussion.
Project and acceptance owner: the user.
Last reviewed: 2026-11-05.

## Problem and users

The user wants hands-on familiarity with voice applications for an interview conversation and wants to exercise a repeatable repository-based development workflow. The proposed product helps a service reviewer decide which callers need follow-up. Source: SRC-001.

Primary prototype user: the project owner demonstrating and evaluating the workflow. A law-firm service reviewer is the proposed end-user persona, not a validated customer.

## Scope and delivery

- Confirmed callback policy v1.0: unresolved issues, outstanding explicit requests, and promises require a callback; clear resolution with no separate obligation and non-actionable calls do not; uncertain cases need review. Sources: SRC-009 and SRC-010.
- Confirmed process: configure the project-workflow orchestrator during intake, before implementation; compare relevant pstack and house skills for substantive tasks. Sources: SRC-007 and SRC-008.
- Confirmed documentation preference: user-flow and architecture diagrams, with supporting diagrams where useful. Source: SRC-005.
- Confirmed: a separate local repository, a draft PRD, audio upload and text inputs, and text-first callback evaluation. Sources: SRC-001 through SRC-004.
- Proposed first demo: prerecorded audio to text, three-way callback recommendation, an evidence excerpt, a review dashboard, and a small independently labeled evaluation set.
- Proposed data: fictional English-language service calls and synthetic or self-recorded audio. No actual customer corpus has been supplied.
- Excluded from the proposed demo: live telephony, autonomous callbacks, CRM integration, legal advice, case qualification, and production operation.
- Success: a clear demo and an honest explanation of requirements, examples, evaluation, mistakes, and iteration.
- Delivery date and deployment target: not specified.

## Stack and system context

No application exists. The web framework, transcription provider, classification model, persistence, hosting, and API credentials have not been selected. The logical flow is proposed in the PRD; it is not an implemented architecture.

Use this stage to settle product behavior. Technical specifications and dependency setup follow selection of an implementation feature. No credentials are needed to author this PRD.

## Assumptions and proposals

| Item | Status | Basis | Consequence |
| --- | --- | --- | --- |
| Audio upload and text transcripts; evaluate decisions on text first | User-selected | SRC-004 | Separate transcription quality from callback decision quality. |
| Browser dashboard | Proposal | SRC-001 suggested a simple dashboard | Keep the interface focused on review and evaluation. |
| Three outcomes and final-resolution boundary | User-accepted | SRC-009 and SRC-010 | Apply callback policy v1.0 to candidate examples. |
| Golden labels require human review | Proposal | Evaluation needs a reference independent of candidate predictions | Model-generated labels remain candidates until reviewed. |
| Fictional English-language data | Proposal | No real corpus or language requirement supplied | Keep the first experiment small and reproducible. |

## Decisions

| ID | Decision | Owner | What it blocks |
| --- | --- | --- | --- |
| D-001 | Resolved: callback policy v1.0 accepted, including the final-resolution boundary and outstanding-obligation exception. | User | No remaining policy blocker for candidate preparation. |
| D-002 | Agent preparation defaults: 40 fictional English cases, user as proposed human reviewer, 20 development and 20 evaluation candidates grouped by family. Final review/freeze pending. | User with agent proposal | Gold release and evaluation claims; preparation may proceed. |
| D-003 | Stack, model provider, and transcription provider | User with implementation recommendation | Executable application and audio integration. |
| D-004 | Minimum acceptable decision quality and review workload | User, informed by baseline results | A claim that the model is fit for a defined use. |
| D-005 | Local demo versus hosted sharing | User | Deployment work only. |

## Intake outcome

The PRD remains a draft for the wider product. F-001 completed the accepted callback policy, labeling guide, and proposed candidate plan. F-002 completed 40 synthetic candidates, a readable review packet, and offline checks. All 40 human label reviews remain pending under F-003. No model has run, and no application acceptance is claimed.
