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

## Evidence records

Keep a short task-local record when a check will be reused across workers or phases. No persistent database or committed log is needed for an ordinary task.

Record the exact command, working directory, observed result, input state, and scope it covers. Input state includes the commit plus relevant staged, unstaged, and untracked files. A commit SHA alone does not identify a dirty checkout. Include relevant test files, configuration, lockfiles, generated artifacts, tool versions, and environment or service state when the check depends on them. Do not record secrets.

Reuse a successful check only when these inputs are unchanged and its scope covers the current acceptance criterion. For a small task, direct inspection of changes since the check is sufficient. If dependencies or input state are unclear, rerun the check. Never treat a timestamp, agent assertion, or prior success on a different checkout as proof.

Invalidate evidence when code, tests, dependencies, configuration, or relevant runtime state changes. Changes outside a proven dependency scope need not invalidate a focused check. Repository-required final checks still apply; do not replace them with a narrower check. A previously failed check needs fresh passing evidence after repair.

After merging worker outputs or grafting arena candidates, verify the integrated artifact. Isolated candidate checks do not cover integration. An external UI or live service check can become stale without a file change; reobserve it when current state matters.

The final answer names the checks and their observed outcome. Report a missing runtime check as a limit, not a pass. Stop when the required checks and material risks are covered; add another check only for a changed input, a failure, or a named uncovered risk.
