---
name: swarm
description: Run independent slices in parallel when their elapsed-time benefit justifies agent and integration cost, or when explicitly requested.
disable-model-invocation: true
---

# Swarm

Name the done predicate and independent slices. Apply the task-wide [efficiency budget](../../docs/efficiency.md). Default to at most two workers total across the task; a requested count takes precedence. Do not split tightly coupled code merely to use workers. Partition by exclusive files or isolated output artifacts.

Use the [delegate contract](../../docs/delegation.md) and current host agent tool. Spawn independent slices concurrently when supported. Each worker verifies its own output and returns concise evidence; no nested delegation by default.

The lead inspects outputs, integrates, and verifies the integrated artifact. Report missing slices as gaps, never passes. Retry only against a specific failure and account for the extra work in the task budget. Synthesize directly, without another agent.

Parallel slices target elapsed time and may increase tokens. For racing competing full implementations, use [arena](../arena/SKILL.md) and declare the selection rule before starting.
