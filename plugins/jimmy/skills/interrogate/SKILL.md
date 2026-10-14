---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Multiple LLM reviewers challenge changes from independent angles."
---

# Interrogate

Spawn independent reviewers to adversarially review code changes. Every reviewer gets the same intent and rubric. Seek model diversity where available. Deliver a synthesized verdict without applying changes.

## Step 1, Scope

Identify what to review from context:

- If the user points at specific files or a diff, use that.
- If on a feature branch, run `git diff main...HEAD` (or the appropriate base branch) for the full changeset.
- If the user's message references recent work, gather the relevant files.

Package the diff or file contents with any surrounding context files the reviewers need to understand the code.

## Step 2, Intent

Before spawning reviewers, state the intent in one clear paragraph from the user's message, commit messages, the PR description if one exists, and the code. If the intent remains uncertain, state the assumption that frames the review.

## Step 3, Spawn Reviewers

Resolve runtime and model preferences per [the Codex runtime reference](../jimmy/references/codex-runtime.md). Reuse the current workflow context in nested skills. Project values take precedence. Missing role lines keep the defaults below. `inherit` and `auto` select an override-capable generic agent with the role lens in its prompt and no model or reasoning override, as the runtime reference specifies.

Use the `interrogate reviewers` configuration line, one seat per entry. By default, use one correctness reviewer and one mechanical reviewer. Add operational and design reviewers when the change has those risks:

| Role | Lens |
|---|---|
| `critic-deep` | Correctness and invariants |
| `critic-fast` | Mechanical issues and missing tests |
| `critic-risk` | Operational failure, retries, rollback |
| `critic-broad` | Design and blast radius |

Launch with `collaboration.spawn_agent` within the available concurrency limit. Reviewers must not edit files. A configured model override uses a compatible configurable agent as described in the runtime reference. If an entry is rejected, retry that seat once using its default role and report the fallback.

Read `references/reviewer-prompt.md` and fill in the same template for every reviewer with the stated intent, the diff or file contents, the rubric from `references/rubric.md`, and the code-quality lens from `references/code-quality-review.md`.

## Step 4, Synthesize

As results come back, build a unified picture. Parse every reviewer's findings. Merge findings that describe the same issue differently, and note which models raised each one. Findings two or more models raised independently are the highest signal. Read a lone model's finding, but weight it accordingly. Note disagreements. If one model flags something and another explicitly says the opposite, that is context for the verdict.

## Step 5, Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. Read `references/lead-judgment.md` for the full framework. Put every finding in one of four buckets, with the model(s) that raised it and a one-line rationale.

- **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. They would block a real PR.
- **Consider**. Legitimate, but you're not sure they outweigh the cost of addressing them now. Worth the user's attention.
- **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact at this stage.
- **Dismissed**. Wrong, nitpicky, or missing context, with a brief reason.

## Output Format

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On
[Each: description, which models raised it, why it matters.]

### Consider
[Each: description, which models raised it, the tradeoff.]

### Noted
[Brief list.]

### Dismissed
[Each with a brief rationale.]

### Agreement Map
[Where models agreed and diverged, and what that pattern tells us.]
