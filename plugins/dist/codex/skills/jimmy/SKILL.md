---
name: jimmy
description: Route software work through Jimmy's concise, risk-scaled workflows and verified results. Use for Jimmy mode, pstack mode, or a request to work in this style.
---

Before following this skill, read [efficiency](../../docs/efficiency.md) and [the host runtime](../../docs/runtime.md) once per workflow context. Their host and routing rules supersede the inherited instructions below.

# Jimmy

Read [the host runtime](../../docs/runtime.md) and [efficiency rules](../../docs/efficiency.md) once per agent and workflow context. The runtime replaces inherited Cursor tool names, paths, model defaults, and unsupported operations. The user's instructions and authorization take precedence. Use only tools and fields exposed in this session.

For a reversible edit with clear ownership and an established design, work directly and run a focused check. For substantive work, pick one playbook and read it before acting. The efficiency rules decide whether its inherited `how`, `architect`, and delegation steps apply. Use [investigation](../jimmy-mode/playbooks/investigation.md) for a read-only answer, [bug fix](../jimmy-mode/playbooks/bug-fix.md) for a reported defect, [feature](../jimmy-mode/playbooks/feature.md) for changed behavior, and [refactoring](../jimmy-mode/playbooks/refactoring.md) for behavior-preserving edits. Use [perf issue](../jimmy-mode/playbooks/perf-issue.md) for measured slowness and [authoring a skill](../jimmy-mode/playbooks/authoring-a-skill.md) for a `SKILL.md` edit. Large migrations use [figure-it-out](../figure-it-out/SKILL.md). Long autonomous work uses [autonomous run](../jimmy-mode/playbooks/autonomous-run.md), and a standing program uses [orchestrate](../jimmy-mode/playbooks/orchestrate.md). Read another playbook only when its trigger applies.

For nontrivial changes, read [how](../how/SKILL.md) to understand ownership before editing. Name the data shape before writing stateful logic. Read a relevant `principle-*` leaf when its trigger applies. In particular, use [Laziness Protocol](../principle-laziness-protocol/SKILL.md) for diff size, [Boundary Discipline](../principle-boundary-discipline/SKILL.md) for adapters, and [Prove It Works](../principle-prove-it-works/SKILL.md) before declaring completion. Read [architect](../architect/SKILL.md) for competing designs or unclear interfaces. A function call alone is not a design fork.

Use [unslop](../unslop/SKILL.md) for prose and [technical writing](../technical-writing/SKILL.md) for documents. Use the host's available skill creator when writing a skill. If none exists, edit the file and validate its frontmatter and links directly. For measured performance claims, read [benchmark checklist](../benchmark-checklist/SKILL.md) before acting on the number.

Keep the lead responsible for review. Delegate only checkable, independent slices through the runtime's actual agent tool. Give file pointers, exclusive ownership, and a testable outcome. Use [swarm](../swarm/SKILL.md) for useful parallel slices and [arena](../arena/SKILL.md) for competing implementations. Do not apply a full orchestration playbook to a routine delegate. Inspect the result yourself.

Verify the real output with the available terminal, browser, app, or service tool. Report `PASS`, `ISSUES`, or `BLOCKED`, the command and observed output, the decision made, and any unresolved limit. Preserve user approval gates and do not send external messages without authorization.
