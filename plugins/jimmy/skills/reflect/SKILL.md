---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

Use `mcp__codex_app__read_thread` for the active thread when its ID is available. Include tool outputs needed to substantiate findings. If chat tools omit needed evidence, use a provided transcript path or a `~/.codex/sessions` entry whose metadata matches this workspace and conversation. Do not search unrelated projects. If no record resolves, write a tight digest of this session and state which evidence it omits.

### 2. Spawn three reviewers in parallel

Launch three reviewers with `collaboration.spawn_agent` within the available concurrency limit. Prompts forbid edits and allow context lookups through enabled tools.

Read [the Codex runtime reference](../jimmy/references/codex-runtime.md) before delegating. Read `.codex/jimmy-models.md` and `~/.codex/jimmy-models.md` on each invocation. Project values take precedence. Missing role lines keep the defaults below. `inherit` and `auto` select an override-capable generic agent with the role lens in its prompt and no model or reasoning override, as the runtime reference specifies.

| Lens | Configuration role | Default `agent_type` | Prompt template |
|---|---|---|---|
| Judgment | `reflect judgment` | `critic-deep` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `critic-fast` | `references/tooling-reviewer.md` |
| Divergent | `reflect divergent` | `critic-broad` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings to the parent through the collaboration tools.

### 3. Synthesize

Spawn with `collaboration.spawn_agent`, using `reflect synthesizer`, default `agent_type: "judge"`. The prompt forbids writes and requires spot-checking citations through enabled tools. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Present backlog items as concrete proposed tickets. File them only when the user has authorized writing to that tracker.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the bundled `skill-creator` skill and validate realistic behavior where needed.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `skill-creator` and check the description against realistic matching and non-matching requests.
- `new skill via skill-creator: <kebab-name>`: hand creation to `skill-creator`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Skip this step if it doesn't.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
