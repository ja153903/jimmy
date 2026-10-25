---
name: arena
description: Compare competing implementations when consequential uncertainty warrants duplicate work, or when the user explicitly requests an arena.
disable-model-invocation: true
---

Before following this skill, read [efficiency](../../docs/efficiency.md) and [the host runtime](../../docs/runtime.md) once per workflow context. Their host and routing rules supersede the inherited instructions below.

# Arena

First identify the uncertainty that sketches or a small experiment cannot resolve. For ordinary design choices, use [architect](../architect/SKILL.md) and implement once. An explicit arena request takes precedence.

State the artifact, acceptance checks, selection rule, and concrete comparison criteria before spawning. Default to two candidates in separate checkouts or output directories, charged against the task-wide [efficiency budget](../../docs/efficiency.md). Use the [delegate contract](../../docs/delegation.md), supported host tools, and valid model preferences. Do not assume model diversity when both candidates inherit the same model.

Candidates receive the same task and constraints without seeing each other's results. The lead inspects the outputs and verification evidence and selects a base against the criteria. No separate judge by default. A requested cross-judge or a named unresolved risk can justify one within the review budget.

Port another candidate's change only when it demonstrably improves the selected result. Grafting is optional, not a required phase. Verify the integrated artifact after any changes. Report the choice, evidence, and any missing candidate; a dropout is not agreement. Fix local defects without rerunning the whole arena unless the decision itself is invalidated.
