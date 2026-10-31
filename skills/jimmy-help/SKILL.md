---
name: jimmy-help
description: Guides users through pstack setup, /jimmy-mode, and picking the skill, playbook, or principle for a task. Type /jimmy-help with a question.
disable-model-invocation: true
---

Read [efficiency](../../docs/efficiency.md) once per workflow context for task-wide budgets and available capabilities.

# Jimmy help

Answer questions about installing Jimmy, selecting a workflow, or using a skill. Read the linked source before describing its behavior. Use local file links when available; do not invent a public URL for modified instructions.

- Installation: read the [package README](../../README.md).
- Start software work: read [Jimmy](../jimmy/SKILL.md). It routes to an investigation, bug fix, feature, refactoring, or performance playbook.
- Understand code: [how](../how/SKILL.md) and [why](../why/SKILL.md).
- Resolve design choices: [architect](../architect/SKILL.md), then an experiment or [arena](../arena/SKILL.md) only when needed.
- Independent work and review: [swarm](../swarm/SKILL.md) and [interrogate](../interrogate/SKILL.md), within the shared efficiency budget.
- Model preferences: [setup-pstack](../setup-pstack/SKILL.md). Without an explicitly configured override, inherit the parent model.
- Verify the application: [create-verification-skill](../create-verification-skill/SKILL.md) or [maintain-verification-skill](../maintain-verification-skill/SKILL.md).
- Unattended work: [autonomous run](../jimmy-mode/playbooks/autonomous-run.md). Future wakeups require an available scheduling tool and authorization.
- Larger programs: [orchestrate](../jimmy-mode/playbooks/orchestrate.md).
- Explore the collection: read the [guide index](../../docs/guide/README.md).

Both hosts install the same skills. Invocation syntax and available tools belong to the current host. Jimmy does not install custom modes, cloud agents, or an automation service. Missing capabilities must be reported rather than simulated with invented tool calls.

Help explains the workflow; it does not start implementation unless the user requests it.
