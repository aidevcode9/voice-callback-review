# How we build

We keep product intent, feature specifications, implementation progress, and verification evidence in the repository. Features move from backlog to active to completed. We choose skills for the work and update documentation alongside code.

This baseline is project-neutral. The [workflow profile](../.codex/workflow-profile.md) supplies the stack, commands, and risks for this project.

## Start with intake

For a new repository, initialize Git locally and record the reviewed intake artifacts in an initial commit. Preserve existing Git history when adopting this process.

1. Inventory available transcripts, statements of work, PRD drafts, and the existing repo in the [source register](../intake/README.md).
2. Establish users, problems, outcomes, scope, stack constraints, integrations, and delivery expectations in the [brief](../intake/PROJECT_BRIEF.md).
3. Create or reconcile the [PRD](PRD.md). Preserve provenance and distinguish drafts from accepted scope.
4. Configure the workflow profile from the actual repo and available skills.
   Configure the scaffolded `project-workflow` orchestrator after initial project classification and scope, before implementation. Compare relevant pstack and house candidates and record the choice.
5. Propose the first feature in backlog. Ask the decision owner about unresolved choices that would change its scope.

Intake is sufficient when the first feature can be specified and verified without guessing a material product decision. Later release questions may remain open with owners. Routine preparation continues within the user's authorization.

## Prepare a feature

1. Choose an unused stable feature ID and a short name.
2. Capture the feature under `features/backlog/` using the [feature templates](../features/README.md).
3. Define observable acceptance criteria and exclusions before coding.
4. Choose one document for a small change or three for a substantial feature.
5. Identify dependencies, affected interfaces, risks, and validation.
6. When the user has selected the work and its blockers are resolved, move the folder to active. Update incoming links.

For a large feature, sequence independently verifiable slices inside the implementation plan. Split into separate features when they have distinct outcomes and acceptance criteria. Keep parent dependencies explicit.

## Select skills for the task

Use the repository profile to select one lead workflow and a few relevant supporting skills. Read the selected instructions. Do not load every installed skill.

The `project-workflow` skill coordinates this selection. For each substantial task, inspect the relevant pstack candidate alongside our own skill. Record the choice and reason in the feature plan or workflow-selection document. Choose based on outcomes, risk, availability, and cost rather than skill origin.

- Bounded features can use a short plan, focused implementation, review, and relevant verification.
- Bounded defects can use an evidence-led debugging loop.
- Hard runtime defects may justify pstack's Bug fix playbook when available.
- Significant design alternatives may justify pstack's architecture exploration.
- Shared contracts, authorization, data changes, and integrations require their affected checks regardless of workflow.

These are starting recommendations. Check the actual installed instructions and tools before choosing. If a full playbook is requested, follow it where applicable and report unavailable steps. If using selected techniques only, describe the method as adapted. Do not silently claim full compliance.

## Implement and keep the record current

1. Inspect existing code and patterns relevant to the feature.
2. Implement the smallest checkpoint with a meaningful verification result.
3. Check that result before starting dependent work.
4. Update progress, deviations, blockers, and the next action in the feature plan.
5. Update living product, architecture, and setup documentation when the change affects them.
   Maintain user-flow and architecture diagrams where they clarify the change, including an explicit distinction between proposed and implemented components.

For bugs, reproduce the failure before fixing it. Eliminate hypotheses with evidence. After the fix, rerun the original reproduction on the same relevant surface. Use a regression check where practical. A passing build alone does not demonstrate the reported behavior.

When pausing, record the current state, last verification result, remaining work, and next action in the implementation plan or the small feature document. A separate status tracker is optional and must not compete with folder lifecycle status.

## Verify and complete

1. Connect every acceptance criterion to an observed result, command, screenshot, stored value, or other relevant evidence.
2. Run the applicable profile checks. Record failures and checks that could not run.
3. Review the change for unintended behavior and documentation drift.
4. Confirm required product acceptance according to this project's profile. Prior authorization remains valid; do not invent a new approval gate for every step.
5. Record known limitations and any explicitly accepted scope changes.
6. Move the folder to completed and update incoming links only when its agreed completion conditions are satisfied.

Completed means the feature's agreed implementation and verification work is finished. Record merge, deployment, and release status separately. If delivery includes deployment, that requirement remains part of completion. Do not move unfinished work to completed because the session ended.

## Maintain the process

Keep the PRD and architecture current. Keep completed feature documents as historical delivery records. Adopt template improvements deliberately. Add enforcement or automation only for a demonstrated recurring problem, and keep checks proportional to the work.
