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

Record the contract and paired cases with `evidence.py contract` before the first edit (see [evidence CLI](#evidence-cli)). Keep the verification choice and [review-trigger](review.md) decision in task state. Before completion, match each obligation to observed evidence or an explicit coverage gap.

## Verification planning

Plan verification during planning, not after implementation.

| Situation | Required action |
| --- | --- |
| Any behavioral change | Trace the real entry point, affected callers, and existing data. Identify what must keep working and verify the most plausible regression through that entry point. Reuse existing checks and project verification skills when they cover it. |
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

## Evidence CLI

`python3 <Jimmy package>/skills/jimmy/scripts/evidence.py` ([source](../skills/jimmy/scripts/evidence.py)) records evidence in any git checkout, from any host or model. Receipts, briefs and reviews go to `<git common dir>/jimmy/records.jsonl`, shared across the repository. Contracts go to `jimmy/records.jsonl` in the recording worktree’s own Git directory. Removing a linked worktree retires its contract. The tree hash covers unstaged edits and deletions (including files flagged skip-worktree or assume-unchanged, outside sparse checkouts) and untracked files that are not ignored.

- `contract --interpretation TEXT --keep CASE [--reject CASE]`: the behavioral contract, before the first edit.
- `receipt -- <cmd>`: run a check; record its exit code and output hash against the tree it ran on.
- `brief` and `review`: independent review; see [review records](review.md#records).
- `status`: the contract, receipts, and reviews for the current tree. Cite it in the final report.
- `gate [--base REV]`: run before delivering HEAD. Each passing receipt for HEAD reruns in its own temporary checkout of that commit. The gate requires a passing receipt and, when the diff from `--base` (default: the upstream merge-base) trips a [review trigger](review.md#independent-review-triggers), a review ending `VERDICT: PASS` that saw the triggered changes.

The gate's triggers are a keyword floor over changed code lines (retries, identity, ownership, cancellation, permissions, migrations, shared state) plus weakened tests (removed or changed assertions, skip or focus markers, deleted test files). Diff attributes and diff configuration cannot hide them. Apply the review policy on top; never argue a fired trigger away.

A passing reviewer must have received the complete patch for **every triggered file** in the delivery. The gate compares the before and after Git blob IDs and file modes for each path with the review brief's recorded contents. An unrelated change or a rebase onto unrelated upstream work preserves coverage. A narrower review of a different patch in the same file needs a fresh review. Use the PR merge base for both review and delivery.

The brief includes both tree IDs and all triggered files, even when their patches exceed the usual size limit. It lists other files omitted for space. An `ISSUES` verdict on an overlapping path blocks delivery until that reviewer gives a covering `PASS`. The verdict must be the final nonblank line. A reviewer command can report `ISSUES` with a nonzero exit. A passing command must exit zero. Older approvals without a record of which patches were shown require a fresh brief and review.

### CI

The [GitHub Actions workflow](../.github/workflows/evidence.yml) runs the package checks against the PR head. A second job starts on a fresh runner, requires the first job to succeed and records a receipt matching the checked-out commit to that tested SHA. It loads the gate from the target branch, compares HEAD with the merge base, and invokes the configured reviewer only when required. A missing reviewer or an unresolved finding fails the job.

The first PR that adds the CLI can pass after the package checks succeed. The evidence job verifies the tested SHA and posts a notice while the CLI is absent from the target branch. Once the CLI lands, subsequent PRs use the target branch's copy. Set the repository variable `JIMMY_REVIEWER` to a reviewer command available on the gate runner that reads the brief from stdin. Use a trusted adapter and isolate provider credentials from processes that execute submitted code. The supplied workflow passes no provider credentials. Protect the workflow and gate through repository rules and require the `evidence` job for merges.

Other CI systems can run the same CLI. Start from fresh evidence, record the trusted check result for the tested SHA, then run `gate --base "$merge_base" --no-rerun`. When review is required, run `review --request "$request" --base "$merge_base" --cmd "$JIMMY_REVIEWER"` and gate again. Keep the gate and its evidence outside the control of the code executing the tests.

Outside a git checkout, state the same facts in the final report.

## Evidence records

Run each check you will cite through `evidence.py receipt`. No other persistent database or committed log is needed.

A receipt records the command, working directory, exit code, output hash, and input state as the working-tree hash; a commit SHA alone does not identify a dirty checkout. Note what the check depends on outside the tree, such as tool versions and environment or service state, and the scope it covers. Receipts keep the end of the output, so do not print secrets in checks.

Reuse a successful check only when its receipt's tree matches the current tree (`evidence.py status`), its other inputs are unchanged, and its scope covers the current acceptance criterion. For a small task, direct inspection of changes since the check is sufficient. If dependencies or input state are unclear, rerun the check. Never treat a timestamp, agent assertion, or prior success on a different checkout as proof.

Invalidate evidence when code, tests, dependencies, configuration, or relevant runtime state changes. Changes outside a proven dependency scope need not invalidate a focused check. Repository-required final checks still apply; do not replace them with a narrower check. A previously failed check needs fresh passing evidence after repair.

After merging worker outputs or grafting arena candidates, verify the integrated artifact. Isolated candidate checks do not cover integration. An external UI or live service check can become stale without a file change; reobserve it when current state matters.

The final answer names the checks and their observed outcome. Report a missing runtime check as a limit, not a pass. Stop when the required checks and material risks are covered; add another check only for a changed input, a failure, or a named uncovered risk.
