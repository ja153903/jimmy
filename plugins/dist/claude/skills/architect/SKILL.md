---
name: architect
description: Compare ownership, interface, or data-model choices before an expensive-to-reverse change.
disable-model-invocation: true
---

Before following this skill, read [efficiency](../../docs/efficiency.md) and [the host runtime](../../docs/runtime.md) once per workflow context. Their host and routing rules supersede the inherited instructions below.

# Architect

Ground only the relevant ownership, callers, and constraints. Reuse existing findings. State the decision to resolve and sketch at most two viable shapes with their public interfaces, data ownership, and tradeoffs. The lead chooses against the acceptance criteria and implements one solution.

A file or function boundary alone does not require this workflow. If the design is established, proceed directly. Do not generate full competing implementations to compare signatures or module placement.

Use a focused experiment for uncertainty sketches cannot answer. Use [arena](../arena/SKILL.md) only when competing implementations are justified or explicitly requested. Use [interrogate](../interrogate/SKILL.md) for a named risk needing independent review. Both consume the shared task budget.

Proceed within the user's scope unless they requested a design checkpoint. If evidence invalidates the chosen design, revise the affected decision; do not automatically restart exploration or a panel. Report the chosen shape, material tradeoff, and verification.
