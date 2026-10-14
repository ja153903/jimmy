---
name: jimmy-help
description: Explain Jimmy setup, workflow routing, skills, playbooks, and principles. Use for jimmy-help or a question about how to use Jimmy.
---

# Jimmy help

Answer the user's question about Jimmy from the installed skills. Read the skill or playbook you recommend before describing it. Give a short prompt the user can reuse when that helps. If the user asks you to perform work, invoke the relevant skill and do it. A help question calls for an explanation, not an unsolicited run.

Resolve the installed Jimmy path from the available skills list. The links below point to files in that plugin. Use a clickable path to the file you read in the reply. Do not guess a public URL or a command this Codex session does not expose.

If the need is unclear, ask whether the user wants setup, to start a task, to pick a skill, to fix a run, or to customize Jimmy. Answer a clear question directly.

## Set up Jimmy

[`setup-jimmy`](../setup-jimmy/SKILL.md) records per-role model and reasoning preferences. Jimmy reads the account file at `~/.codex/jimmy-models.md` and the project's `.codex/jimmy-models.md` when present. A missing preference uses the skill's default. Setup validates choices against the models and agent roles actually available in the session. Read [the Codex runtime reference](../jimmy/references/codex-runtime.md) before explaining role settings or agent tools.

A project verification skill gives an agent a scripted way to drive an app. When the question is about proving a change, inspect the project's existing `verify-*` skill or harness first. If it lacks one, point to [`create-verification-skill`](../create-verification-skill/SKILL.md).

## Start a task

[`jimmy`](../jimmy/SKILL.md) selects a playbook, keeps its steps in a todo list, and invokes narrower skills as needed. A useful request states the outcome, the evidence that would prove it, and any constraints. See [`references/prompting.md`](references/prompting.md) for examples. Jimmy applies to the task where invoked. To keep using it on later tasks, invoke it again or ask Codex to keep the same style.

Playbooks are files under [`jimmy/playbooks`](../jimmy/playbooks), not separate slash commands. The Jimmy skill's Playbooks section maps a task to one. Examples include Bug fix, Feature, Investigation, Eval, Babysit, Shipping, and Session pickup. A request to check a PR uses Babysit; a request to land it uses Shipping. A request for only a plan uses Multi-phase plan.

Jimmy principles are small skills under `principle-*`. The Jimmy skill names when each applies. The agent reads the relevant leaf file and reports which decision it changed. The user can invoke one directly when they want to emphasize that rule.

## Pick a skill

Recommend the narrowest skill for the request. Read its current frontmatter and instructions before recommending it. The table covers common choices; other installed skills may also apply.

| The user wants to | Skill |
|---|---|
| Use Jimmy's full workflow | [`jimmy`](../jimmy/SKILL.md) |
| Check the agent's understanding | [`in-your-own-words`](../in-your-own-words/SKILL.md) |
| Understand code behavior or placement | [`how`](../how/SKILL.md) |
| Learn the reasons behind a design | [`why`](../why/SKILL.md) |
| Get one plain explanation of how and why | [`teach`](../teach/SKILL.md) |
| Rebuild context across recent tasks | [`recall`](../recall/SKILL.md) |
| Catch up on this chat | [`ketchup`](../ketchup/SKILL.md) |
| Review a small change's wider effects | [`blast-radius`](../blast-radius/SKILL.md) |
| Settle types and module shape before code | [`architect`](../architect/SKILL.md) |
| Compare independent attempts at one brief | [`arena`](../arena/SKILL.md) |
| Split independent checks or work | [`swarm`](../swarm/SKILL.md) |
| Challenge a diff from several review lenses | [`interrogate`](../interrogate/SKILL.md) |
| Review comments and unsupported workarounds | [`no-comments`](../no-comments/SKILL.md) |
| Apply the writing standard | [`technical-writing`](../technical-writing/SKILL.md) |
| Cut AI prose patterns | [`unslop`](../unslop/SKILL.md) |
| Restate the last reply plainly | [`bro`](../bro/SKILL.md) |
| Vet a measured performance claim | [`benchmark-checklist`](../benchmark-checklist/SKILL.md) |
| Design a rigorous run when no playbook fits | [`figure-it-out`](../figure-it-out/SKILL.md) |
| Record decisions during a long run | [`show-me-your-work`](../show-me-your-work/SKILL.md) |
| Configure role preferences | [`setup-jimmy`](../setup-jimmy/SKILL.md) |
| Turn working preferences into a skill | [`automate-me`](../automate-me/SKILL.md) |
| Capture durable lessons from a task | [`reflect`](../reflect/SKILL.md) |

Close calls are described in [`references/recipes.md`](references/recipes.md). In particular, `how` explains what code does, `why` investigates reasons, and `teach` combines them. `arena` gives agents the same brief; `swarm` splits work into parts. `recall` searches relevant prior tasks; `ketchup` covers this chat since the last user message.

## Fix a run

Inspect the actual skill, tool result, and task state before diagnosing a stalled or misrouted run. A missing agent role or model preference does not prove the workflow failed; the runtime reference gives the fallback. If a verification skill is absent, the agent may still drive the app with available tools. If the user asks whether a change works, verify the real behavior rather than citing a green build.

Jimmy has no persistent Custom Mode hook or Cursor `/loop` command in Codex. A request to keep working in this session is handled through the active task. A recurring follow-up requires an available scheduler and the user's authorization. A separate task is created only when the user asks for one.

## Make Jimmy your own

Use [`automate-me`](../automate-me/SKILL.md) for a personal style skill and [`reflect`](../reflect/SKILL.md) for lessons from an actual task. Use Jimmy's Authoring a skill or Eval playbook for a new or changed reusable skill. The bundled Codex `skill-creator` governs skill authoring and validation.

Lead the reply with the answer. Give at most one adapted example prompt from [`references/recipes.md`](references/recipes.md), then link the skill or playbook that supports it. Expand into a catalog only when the user asks for the whole map.
