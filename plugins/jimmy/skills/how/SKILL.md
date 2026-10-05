---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Can critique architecture. Use why for motivation."
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Read [the Codex runtime reference](../jimmy/references/codex-runtime.md) before delegating. Read `.codex/jimmy-models.md` and `~/.codex/jimmy-models.md` on each invocation. Project values take precedence. Missing role lines keep the defaults below. `inherit` and `auto` select an override-capable generic agent with the role lens in its prompt and no model or reasoning override, as the runtime reference specifies.

## Step 1. Assess Complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. One explainer explores and explains in a single pass. Go to Step 2b.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): spawn parallel explorers first, then hand off to the explainer. Go to Step 2a.

When in doubt, take the simple path.

## Step 2a. Explore (complex questions only)

Decompose the question into 2 to 4 exploration angles, each a distinct slice of the subsystem. Launch explorers within the available concurrency limit:

- Tool: `collaboration.spawn_agent`.
- Configuration role: `how explorer`, default `agent_type: "worker-fast"`.
- The prompt forbids writes.

Each explorer gets the prompt in `references/explorer-prompt.md` with its angle filled in. Then go to Step 3.

## Step 2b. Direct Explain (simple questions)

Spawn one subagent that explores and explains in one pass:

- Tool: `collaboration.spawn_agent`.
- Configuration role: `how explainer`, default `agent_type: "worker-deep"`.
- The prompt forbids writes.

Build its prompt from `references/explainer-prompt.md` without the explorer-findings section. Go to Step 4.

## Step 3. Synthesize (complex questions only)

Once all explorers have returned, spawn one subagent to synthesize their findings into one explanation:

- Tool: `collaboration.spawn_agent`.
- Configuration role: `how explainer`, default `agent_type: "worker-deep"`.
- The prompt forbids writes.

Build its prompt from `references/explainer-prompt.md` with every explorer's findings filled in.

## Step 4. Present

Present the explainer's output to the user. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output Format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.

## Critique mode

When the user asks for architectural issues or improvements, explain the architecture first using the flow above. Then read `references/critic-prompt.md` and `references/critique-rubric.md`.

Use the `how critics` configuration line. Defaults are `critic-risk`, `critic-deep`, `critic-broad`, and `critic-fast`. Spawn each with `collaboration.spawn_agent` and a read-only prompt, within the available concurrency limit. Give each critic the explanation, relevant source paths, and rubric. Preserve their distinct operational, correctness, design, and mechanical lenses.

Lead judgment uses the framework in `../interrogate/references/lead-judgment.md`. Classify findings as Act on, Consider, Noted, or Dismissed. Present the explanation first, then the critique verdict.
