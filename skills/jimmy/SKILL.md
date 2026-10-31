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

Use [architect](../architect/SKILL.md) for unclear ownership or consequential interface choices. Compare short sketches before implementing once. Use [swarm](../swarm/SKILL.md), [interrogate](../interrogate/SKILL.md), or [arena](../arena/SKILL.md) only for their escalation triggers or an explicit request. Apply the task-wide budgets in efficiency across these workflows.

Read principle leaves only for an unresolved decision they materially affect. Do not produce a separate onboarding explanation before routine implementation. Use [how](../how/SKILL.md) and [why](../why/SKILL.md) when their questions need answering.

For a property that ordinary tests cannot adequately cover, such as a race or retry invariant, use [Create a formal verification skill](../create-formal-verification-skill/SKILL.md). Use [Maintain a formal verification skill](../maintain-formal-verification-skill/SKILL.md) when covered code has drifted. Choose one valuable property, state the bounds, and prove the check catches a broken variant; formal verification is not a routine gate for every change. For TLA+ results, use [Statechart](../statechart/SKILL.md) to explain behavior and counterexamples.

Large migrations can use [figure-it-out](../figure-it-out/SKILL.md); sustained autonomous work can use [autonomous run](../jimmy-mode/playbooks/autonomous-run.md) or [orchestrate](../jimmy-mode/playbooks/orchestrate.md). These routes retain the available capabilities, task-wide budgets, and user authorization.

Verify the actual artifact. Report PASS, ISSUES, or BLOCKED, the outcome, commands and observed results, and any unresolved limit. Do not claim measured performance improvements without measurement.
