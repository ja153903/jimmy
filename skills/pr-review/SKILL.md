---
name: pr-review
description: Review a PR, branch, or final implementation diff for correctness and concrete maintainability costs, with evidence, composition checks, and explicit verification limits.
---

# PR review

Return actionable findings and an honest account of coverage. Use this procedure for requested reviews and the lead's final implementation review. A standalone review produces findings without repairs. An implementation review retains its authority to fix in-scope violations.

## Establish the review contract

Apply the shared [review policy](../../docs/review.md), [verification evidence](../../docs/verification.md), and [efficiency rules](../../docs/efficiency.md). Preserve explicitly configured review limits and host model preferences. A findings-only review defaults to static inspection unless the user authorizes execution. Carry command limits, review scope, and authorized writes into reviewer briefs. Review preferences do not weaken required implementation checks.

Identify the target, base, head, and intended behavior from the request, PR description, linked requirements, and repository instructions. Check the author's interpretation against the requirements. Record inaccessible requirements and consequential ambiguity as coverage gaps. For a stack, use the actual parent as the base and account for earlier dependencies.

Record commit IDs and relevant working-tree state. For local and implementation reviews, inspect the complete final diff, including staged, unstaged, untracked, and delegated changes. Distinguish local changes from the published PR. Do not silently review a stale head or omit an untracked implementation file.

## Inspect behavior and consequences

Trace affected callers, contracts, ownership, and state transitions beyond the changed lines. Identify regressions introduced or exposed by the change. Report unrelated pre-existing problems separately only when material, with their provenance.

Check the boundary the tests actually exercise. Look for synchronous mocks replacing deferred completion, omitted ownership providers, transformed inputs validated but not consumed, and smoke checks that bypass the production loader or consumer. A test count does not establish those guarantees. Apply findings across the affected diff and analogous paths rather than only the examples named in an earlier round.

Scale depth to the affected behavior. For permissions, migrations, retries, identity, cancellation, and shared state, trace relevant valid and invalid cases, event ordering, partial failures, and recovery. Check compatibility with existing callers, persisted data, and mixed versions when applicable. A wording-only change does not need a lifecycle audit.

Record whether [review policy](../../docs/review.md) requires independent review and why. When triggered, use [interrogate](../interrogate/SKILL.md) under the same scope and evidence standard. Another pass by the same agent is not independent. Report unavailable required independence without claiming review completion.

## Check composition and engineering taste

Apply repository rules and [Functional Composition](../principle-functional-composition/SKILL.md). Record a relevant file or symbol and result for each area, or a concrete reason it does not apply:

| Area | What to inspect |
| --- | --- |
| Domain purity and explicit inputs | Decisions receive relevant values explicitly. Time, randomness, configuration, and hidden state do not silently determine their results. |
| Visible side effects | Callers visibly coordinate reads, writes, logging, and transactions. Helpers do not conceal effects behind apparent calculations. |
| Caller-owned data | Functions preserve inputs unless mutation is part of their explicit contract. Local mutation of fresh data is allowed. |
| Responsibility boundaries | Functions, components, hooks, and modules isolate understandable responsibilities. Avoid pass-through layers, scattered domain assumptions, and duplicate sources of truth. Clear loops and simple inline expressions are allowed. |

Enforce engineering taste when it follows an applicable rule or has a concrete maintenance cost. Name what becomes harder or less reliable, where the cost occurs, and a simpler change that addresses it. Consider constraints and tradeoffs before recommending restructuring. A small helper can clarify one responsibility even with one caller.

Do not flag equivalent loop styles, naming preferences, file length alone, or hypothetical future flexibility. Do not demand a rewrite merely because another design is possible. A minor rule violation is not automatically a blocker. Companion review lenses do not lower this evidence bar or override the findings filter.

## Assess verification

Inspect tests for the changed behavior, boundary cases, and meaningful failure paths. Check whether assertions would detect the claimed regression. Passing tests alone do not establish correctness.

Identify applicable existing lint, type, and architecture checks from repository instructions and executable configuration. Run them for implementation completion. For findings-only review, run only what the execution policy permits. Inspect commands and prerequisites first. Do not install dependencies or alter the environment merely to expand coverage.

Record executed commands, working directory, scope, reviewed input state, and observed results. Distinguish checks you ran from author claims and existing CI evidence. Reuse evidence only while relevant inputs remain unchanged. Missing, unavailable, or prohibited checks are gaps, not passes. Do not label failures pre-existing without baseline evidence.

## Validate and prioritize findings

Check each candidate against actual code and reachable callers. Merge duplicate root causes. Each finding includes:

- Severity and precise source location, preferably the smallest relevant changed range.
- Triggering condition, expected behavior, actual failure or maintenance cost, and practical impact.
- Supporting code, an applicable rule, or observed evidence. Distinguish static reasoning from executed reproduction.
- A focused correction or simpler alternative when useful, without repairs during findings-only review.

Use repository severity conventions. Otherwise use P0 for an immediate critical issue, P1 for a serious issue requiring prompt correction, P2 for an actionable defect or material maintainability cost, and P3 for a minor issue. Severity follows demonstrated impact. State whether a finding prevents approval and why. Keep optional improvements separate from blockers.

Apply the findings filter. Under `correctness`, omit taste-only findings. Under `all`, require the same concrete cost or repository rule for maintainability feedback. Discard subjective preferences and unsupported speculation. Keep material unresolved security, migration, concurrency, or data-loss risks visible with the exact missing evidence. Do not present those risks as confirmed defects.

## Complete the review

Recheck fixes and affected behavior after authorized edits. Refresh the relevant diff and evidence after head, base, or working-tree changes. Do not restart an entire panel unless the change warrants it.

Keep the lead's reviewed input and findings in task state and the handoff. For a standalone findings-only review, return the findings without executing the evidence CLI or writing records unless separately authorized. The orchestrator records actual independent reviews with the [evidence CLI](../../docs/verification.md#evidence-cli) under the shared [review records](../../docs/review.md#records), binding them to the exact briefs the independent reviewers received. Do not submit a lead self-review as an independent review record. A lead review does not satisfy required independence or replace the delivery gate.

Return findings first, ordered by severity, followed by a concise review record:

- Reviewed base, head, local state, and scope.
- Results for the four composition areas, with file or symbol evidence or an explanation of non-applicability.
- Commands and outcomes, evidence reused, and coverage gaps.
- Unresolved violations, justified exceptions, material risks, and anything preventing approval.

An empty findings list is valid. Say "no findings" within the reviewed scope and disclose verification limits. Do not imply approval while required evidence or review remains unavailable. AI review is judgment, not proof. Do not claim hooks or CI enforcement unless configured and verified. Prefer scoped deterministic rules for recurring mechanical violations when tooling changes are authorized.

A verdict does not authorize source repairs, commits, pushes, GitHub comments, formal approval, CI retries, monitoring, or merging. Perform those actions only when separately authorized by the task.

Adapted from [figma/jimmy PR review](https://github.com/figma/jimmy/blob/1a941381334cf8683a4e0814fc759baf0e873852/skills/pr-review/SKILL.md). The package retains the upstream MIT license in [LICENSE](../../LICENSE).
