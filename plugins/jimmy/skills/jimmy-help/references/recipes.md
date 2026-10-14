# Requests worth copying

Replace placeholders with the real target and checks. Adapt the request to the task rather than copying its exact wording.

## Understand

- `$jimmy Read <issue>. Restate the underlying problem in your own words. Do not change code yet.`
- `$jimmy Investigate why <symptom> happens. Cite the code and history. Keep this read-only.`
- `$how Explain how <subsystem> works and where a change to <behavior> belongs.`
- `$recall Catch me up on my recent work on <topic>, then read <issue>.`
- `$jimmy Take over <branch>. Identify completed work, verify its state, and continue without repeating it.`

## Build

- `$jimmy <symptom>. Reproduce it first, then fix it and show the observed result.`
- `$jimmy Add <behavior>. Preserve <specific existing behavior> and verify both paths.`
- `$jimmy Move <code> into one module without changing output. Capture the current output first and compare after.`
- `$jimmy <operation> takes <time> on <fixture>. Measure the cause, fix it, and show before and after results.`

## Design and plan

- `$jimmy Prototype a few options for <feature>. Show the outputs so we can compare them.`
- `$architect Sketch the types and module boundaries for <feature>. Let me review the design before implementation.`
- `$jimmy Turn <settled design> into a plan of small changes, each with a verification step.`
- `$jimmy Plan the migration from <source> to <target>. Preserve the current behavior, including known quirks.`

## Review and ship

- `$interrogate Review this branch for real bugs and regressions. Give a verdict without editing it.`
- `$swarm Check each package under <directory> against its own check script and return one report.`
- `$jimmy Open a PR for this change with verification evidence.`
- `$jimmy Check on PR <number> and address anything needed to make it merge-ready.`
- `$jimmy Land the verified stack.`

## Away and back

- `$jimmy I am stepping away. Work on <goal> until <checks pass>. Use a fresh worktree from <base> and keep a decision trail. Stop only at <named gate>.`
- `$show-me-your-work Summarize the decisions from the run and point me to their evidence.`
- `$reflect Identify durable lessons from this task and propose specific skill changes.`
- `$ketchup Catch me up on what changed in this chat since my last message.`
