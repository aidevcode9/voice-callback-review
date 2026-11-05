# Prepare a project for its first feature

Use existing evidence before asking questions. A short transcript can be enough to start a small project. Missing paperwork does not justify manufacturing a statement of work or an approved PRD.

## Collect the inputs

Record a source ID, title, date or unknown date, location, and authority in `intake/README.md`. Link private files by local path or approved source-system link. Avoid copying restricted material into tracked Markdown.

The skeleton provides ignored folders for transcripts, statements of work, and PRD drafts. Their existence is optional evidence storage, not a requirement to produce every artifact. Source files stay unchanged. Synthesize relevant facts in the brief with source IDs and page, section, or timestamp references where available.

When sources disagree, record both claims and ask the decision owner if the difference changes the product. A later conversation does not automatically supersede a signed delivery commitment.

## Establish the brief

Resolve these groups as far as the sources allow:

| Group | Questions |
| --- | --- |
| Purpose | Who experiences the problem? What outcome would make this project useful? |
| Scope | What is the first release? What is excluded? Is this a prototype, an internal tool, or a maintained product? |
| People | Who uses it, who decides scope, and who accepts delivery? |
| Stack | What exists? Which languages, frameworks, hosting, and runtime constraints are required? Which choices remain proposals? |
| Data and integrations | Which inputs, external systems, credentials, data boundaries, and access rules matter? Record credential names or setup needs, never values. |
| Delivery | What dates, operational expectations, support obligations, and measurable outcomes apply? |
| Verification | Which real user flows must work? Which commands and environments can demonstrate them? |

For each unresolved item, record its owner and whether it blocks intake completion, a particular feature, or release. An unknown release detail need not block a reversible first feature.

## Reconcile the PRD

If a usable PRD exists, preserve its content and map it to `docs/PRD.md` without silently changing commitments. If it is a draft, label the working PRD as a draft. If none exists, derive a draft from the brief.

Give requirements stable IDs. Each initial feature references the product requirements it serves and adds concrete acceptance criteria. Keep product choices in requirements, system design in the technical specification, and task sequencing in the implementation plan.

## Choose the workflow

Inspect installed skills and read the relevant entrypoints before recommending them. Evaluate fit, tool availability, risk, and execution cost. Reputation is a reason to inspect a method, not evidence that it performs better.

The scaffold includes `project-workflow`. Configure that project orchestrator after identifying the project type and initial scope, before starting implementation. Keep exact checks and skill availability in the repository profile. For each substantial task, compare the relevant pstack and house candidates and record the choice. Revisit the choice as the task changes.

- Default to a bounded plan, focused implementation, review, and relevant verification.
- For hard runtime bugs, consider pstack's Bug fix playbook if available. Its reproduction, hypothesis elimination, and matching-surface verification are valuable beyond a small test failure.
- For a significant architecture choice, consider pstack's design exploration if the alternatives and extra review justify the work.
- For database, authorization, shared interfaces, or external integrations, name the affected invariants and checks in the repository profile regardless of lead workflow.
- If an explicitly requested workflow requires unavailable tools or models, report the limitation. An adapted method must be labeled as adapted. Do not claim the full playbook ran.

Pstack is optional. The template does not bundle or install it. Instructions to create PRs or run deployment steps remain subject to the user's authorized scope.

## Finish intake

The output is a reviewable brief, a working PRD with its status stated, a configured project orchestrator and profile, and a first feature proposal. Include useful user-flow and architecture diagrams. Update `intake/PROJECT_BRIEF.md` to record what can start and what is blocked. Leave decisions unresolved when the evidence cannot settle them. Do not stop merely to ask whether to create already-requested documents.

When the task includes creating a new repository, initialize Git locally and review the staged files before the initial commit. Preserve the history of existing repositories. Keep raw source material in its approved location or ignored intake folders. Remote publication remains a separate action governed by the user's request.
