# Verification

## Behavioral contract

Before implementation, derive expected behavior from the user's request and the surrounding supported flows. A bug reproduction identifies one failing case, not the complete contract.

Before adding or changing a retry, identity, ownership, permission, or cancellation guard, answer:

> What ordinary event can change the value this guard checks without invalidating the user's operation?

Trace the operation's lifetime separately from the lifetime of the session, component, connection, or object used to represent it.

Derive paired cases:

- A supported operation that must remain valid across a relevant ordinary event.
- A replaced, skipped, cancelled, or unauthorized operation that must be rejected.

Choose cases that distinguish the intended condition from an overly broad substitute. Verify both outcomes with the cheapest faithful checks.

Example: if the contract allows retries after navigation or reconnection, session recreation must not invalidate the pending operation. Replacing or skipping that operation must still invalidate it. A guard keyed on session identity fails the first case; deleting the guard fails the second.

Keep the contract, paired cases, verification choice, and [review-trigger](review.md) decision in task state. Before completion, match each obligation to observed evidence or an explicit coverage gap.

## Verification planning

Plan verification during planning, not after implementation.

| Situation | Required action |
| --- | --- |
| Any behavioral change | Identify the affected user journey, observable result, existing checks, and relevant project verification skills. |
| Affected journey lacks a repeatable real-app check | Use [create-verification-skill](../skills/create-verification-skill/SKILL.md) to establish focused coverage, including in an existing project. |
| Journey already has verification instructions | Update and exercise the affected entries with the implementation. |
| Ordering, retries, ownership, or shared state changes | State the invariant, relevant events, user harm, and which event orderings the chosen checks cover. |
| Concrete harmful orderings remain inadequately covered by tests | Reuse suitable formal verification or use [create-formal-verification-skill](../skills/create-formal-verification-skill/SKILL.md). |
| Formally covered code or assumptions change | Confirm that the verification still describes the code before treating its result as evidence; see [maintain-formal-verification-skill](../skills/maintain-formal-verification-skill/SKILL.md). |
| Tool or environment is unavailable | Complete independent checks and report the precise remaining gap. |

A topic alone does not require a formal model. Explain why empirical checks sufficiently cover the property, or identify what they leave uncovered. Generated-input tests are empirical evidence, not formal proof.

The linked generator skills are explicit-only for implicit routing; when a row requires one, open its SKILL.md and follow it.

## Network failure and recovery

For affected network-dependent journeys, select failures from the requests the journey actually makes. Cover connection failure, stalled requests reaching their timeout, and applicable transient server errors or rate limits.

For mutations, also cover a server commit whose response never reaches the client. A rejected request does not exercise this uncertain outcome.

Inject faults deterministically at an existing boundary in an isolated test environment. Drive the real user entry point. Observe the error, completion time, preserved input and durable state, bounded retries, and supported recovery.

After an uncertain write and any supported retry, inspect server-side state for duplicate effects. Restore fault injection during cleanup, including after failed attempts.

Record expected and observed behavior, fault timing, recovery, and durable state. Report unavailable injection or observation as coverage gaps. Mark journeys without network dependencies as not applicable.

## Evidence records

Keep a short task-local record when a check will be reused across workers or phases. No persistent database or committed log is needed for an ordinary task.

Record the exact command, working directory, observed result, input state, and scope it covers. Input state includes the commit plus relevant staged, unstaged, and untracked files. A commit SHA alone does not identify a dirty checkout. Include relevant test files, configuration, lockfiles, generated artifacts, tool versions, and environment or service state when the check depends on them. Do not record secrets.

Reuse a successful check only when these inputs are unchanged and its scope covers the current acceptance criterion. For a small task, direct inspection of changes since the check is sufficient. If dependencies or input state are unclear, rerun the check. Never treat a timestamp, agent assertion, or prior success on a different checkout as proof.

Invalidate evidence when code, tests, dependencies, configuration, or relevant runtime state changes. Changes outside a proven dependency scope need not invalidate a focused check. Repository-required final checks still apply; do not replace them with a narrower check. A previously failed check needs fresh passing evidence after repair.

After merging worker outputs or grafting arena candidates, verify the integrated artifact. Isolated candidate checks do not cover integration. An external UI or live service check can become stale without a file change; reobserve it when current state matters.

The final answer names the checks and their observed outcome. Report a missing runtime check as a limit, not a pass. Stop when the required checks and material risks are covered; add another check only for a changed input, a failure, or a named uncovered risk.
