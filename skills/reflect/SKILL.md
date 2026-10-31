---
name: reflect
description: Review the active conversation for recurring, evidence-backed lessons and propose concrete skill edits. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Review the current conversation for recurring, evidence-backed lessons. A one-off or an issue already covered by guidance the agent ignored does not justify a new rule.

Use the conversation context, an exposed history tool for this chat, or an exact supplied transcript path. If raw history is unavailable, use a scoped digest and disclose the evidence limit. Do not select a guessed newest transcript.

Consider the [judgment](references/judgment-reviewer.md), [tooling](references/tooling-reviewer.md), and [divergent](references/divergent-reviewer.md) lenses. Apply the task-wide [efficiency budget](../../docs/efficiency.md). Use a bounded independent reviewer when justified or explicitly requested; otherwise review directly and disclose missing independence. Give delegates the transcript or digest and relevant lens, using supported roles and inherited models by default.

Synthesize Accepted / Rejected / Backlog findings using the criteria in the [synthesizer brief](references/synthesizer.md). Spot-check citations. Prefer a correction to an existing skill over creating a new skill; prefer a structural check when it can enforce the property reliably.

Show concrete proposed edits and their destinations before requesting any approval that is still needed. Honor existing authorization. Apply only changes within the user's scope. File backlog items externally only when explicitly authorized.

Edit maintained source, never an installed cache. Use an available skill creator for substantive skill changes, or edit directly when none exists. Validate frontmatter and local links, inspect the resulting instructions, and exercise realistic requests when behavior changes.

Report edits applied, evidence, deferred findings, and remaining limits. Do not push or open a PR unless requested.
