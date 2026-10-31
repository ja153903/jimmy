# Efficient Jimmy workflows

## Default path

Inspect relevant code, implement one solution, run focused verification, review the diff, and finish. The lead owns this path. A task spanning several files does not by itself need delegation or design exploration. Load one relevant playbook for substantive work; load additional skills only to resolve a specific question. Reuse unchanged instructions and findings within this workflow context.

## Available capabilities

Use the current session's native tools and supported schemas. Delegate a bounded task through an exposed agent tool, with a registered role or the role lens in the brief; Markdown reference files do not register roles. Without delegation, work directly and disclose any missing independent review. Do not guess model aliases, background fields, cloud execution, or isolation support.

Use discoverable skill locations from the current host's instructions when authoring skills. Read model preferences only from an explicitly configured location, and only when selecting a delegate; inherit the parent when no supported override exists. Retrieve chat history only through an exposed tool for the intended chat or an exact supplied transcript path.

Future wakeups need an exposed scheduling tool and authorization for recurring work. If absent, finish the active session's work and report the next action and continuation limit. Use the repository's real checks and verify actual PR state through an available forge tool or CLI. A skill cannot grant an unavailable capability or authorize external messages, publishing, or merging.

## Escalation and budgets

Start with zero delegates, one implementation, and one review pass. These are workflow defaults, not runtime-enforced quotas. User requests and repository-required checks take precedence.

Escalate against a named question or risk:

- Unclear ownership or an expensive-to-reverse interface: compare at most two short design sketches in the lead, choose, then implement once. Use [architect](../skills/architect/SKILL.md).
- Independent work with disjoint outputs that repays startup and integration: use at most two workers total across the task. Use [swarm](../skills/swarm/SKILL.md). Parallelism targets elapsed time and may increase total tokens.
- A concrete correctness, security, migration, or concurrency risk needing another perspective: use one independent reviewer and one review round. Give the reviewer that risk and the relevant diff. Use [interrogate](../skills/interrogate/SKILL.md).
- Competing implementations would resolve consequential uncertainty that sketches or a small experiment cannot: use [arena](../skills/arena/SKILL.md), with two candidates and lead selection. An arena uses the worker budget, not a separate allowance.

Budgets apply to the whole task, not separately to each phase or delegate. Delegates do not spawn more agents by default. Before exceeding a default, state the unresolved question, evidence that existing work cannot answer it, the additional work, and its stopping condition. Continue within existing authorization; a budget increase alone does not require permission. Explicit panel sizes and exhaustive investigations override the matching default. Do not quietly replace an explicit independent review with self-review.

A failed check requires diagnosis and repair, not abandonment to meet a budget. Recheck the fix and affected behavior. Avoid restarting whole panels for a local defect. When progress depends on missing access or user input, report the precise gap.

## Context and models

Use the [delegate contract](delegation.md) for compact briefs and results. Do not pass the full conversation by default. Ground once and reuse file pointers and a short finding summary; reopen changed files or investigate unresolved evidence. The lead synthesizes results directly, without a separate explainer or judge by default.

Read host model preferences only when selecting a delegate. Default to inheritance and supported tools. Honor valid configured model and effort choices. If choosing an effort level, use the lowest exposed level appropriate to the slice and raise it for demonstrated difficulty. Do not impose fixed expensive reviewer roles on routine work. A cheaper model is useful only if it can complete the slice without repeated repair.

## Verification and finish

Use [verification evidence](verification.md) to reuse checks only while their inputs remain valid. Complete repository-required checks. Finish when the acceptance criteria and material risks are covered; do not repeat checks for each workflow phase. Keep the final report to the outcome, commands and observed results, and unresolved limits. Report measured savings only with host usage and elapsed-time evidence, including delegates.
