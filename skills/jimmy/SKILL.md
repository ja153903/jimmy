---
name: jimmy
description: Route software work through Jimmy's concise, risk-scaled workflows and verified results. Use for Jimmy mode, pstack mode, or a request to work in this style.
---

# Jimmy

Read [efficiency](../../docs/efficiency.md) once per workflow context. Use the current session's tools and preserve the user's scope and authorization.

The lead inspects, implements one solution, verifies, and reviews the diff. For a reversible edit with clear ownership, work directly and run a focused check. For substantive work, read one matching playbook:

- [Investigation](../jimmy-mode/playbooks/investigation.md) for a read-only answer.
- [Bug fix](../jimmy-mode/playbooks/bug-fix.md) for a defect.
- [Feature](../jimmy-mode/playbooks/feature.md) for changed behavior.
- [Refactoring](../jimmy-mode/playbooks/refactoring.md) for behavior-preserving changes.
- [Perf issue](../jimmy-mode/playbooks/perf-issue.md) for measured slowness.
- [Skill authoring](../jimmy-mode/playbooks/authoring-a-skill.md) for SKILL.md edits.

Use [architect](../architect/SKILL.md) for unclear ownership or consequential interface choices. Compare short sketches before implementing once. Use [swarm](../swarm/SKILL.md) or [arena](../arena/SKILL.md) only for their escalation triggers or an explicit request. Apply the task-wide budgets in efficiency across these workflows.

Read and apply the [review policy](../../docs/review.md) during planning and again before completion; budgets never waive it. When it requires independent review, open [interrogate](../interrogate/SKILL.md) and follow it; do not wait for implicit skill invocation. Before changing a retry, identity, ownership, permission, or cancellation guard, derive the [behavioral contract](../../docs/verification.md#behavioral-contract) and its paired cases.

When the change touches `.ts` or `.tsx`, read and apply [TypeScript best practices](../typescript-best-practices/SKILL.md) before implementing and again when reviewing the diff. Its type rules are correctness requirements and outrank diff size and simplification. Read other principle leaves only for an unresolved decision they materially affect. Do not produce a separate onboarding explanation before routine implementation. Use [how](../how/SKILL.md) and [why](../why/SKILL.md) when their questions need answering.

During planning for any behavioral change, read and apply [verification planning](../../docs/verification.md#verification-planning), including [network failure and recovery](../../docs/verification.md#network-failure-and-recovery) for network-dependent journeys. When it requires a generator, open and follow that skill's SKILL.md directly: [create-verification-skill](../create-verification-skill/SKILL.md) for a journey without a repeatable real-app check, [create-formal-verification-skill](../create-formal-verification-skill/SKILL.md) for harmful orderings tests leave uncovered, or [maintain-formal-verification-skill](../maintain-formal-verification-skill/SKILL.md) when covered code has drifted. Formal verification needs a concrete uncovered ordering, not a topic: choose one valuable property, state the bounds, and prove the check catches a broken variant. For TLA+ results, use [Statechart](../statechart/SKILL.md) to explain behavior and counterexamples.

Large migrations can use [figure-it-out](../figure-it-out/SKILL.md); sustained autonomous work can use [autonomous run](../jimmy-mode/playbooks/autonomous-run.md) or [orchestrate](../jimmy-mode/playbooks/orchestrate.md). These routes retain the available capabilities, task-wide budgets, and user authorization.

Verify the actual artifact. Report PASS, ISSUES, or BLOCKED, the outcome, commands and observed results, and any unresolved limit. Also report the review trigger decision and how independent review ran (or that it is missing), and, for ordering, retry, ownership, or shared-state changes, whether formal verification would add coverage and why. Do not claim measured performance improvements without measurement.
