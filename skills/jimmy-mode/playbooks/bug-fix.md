### Bug fix

The lead reproduces the defect, identifies its mechanism, implements, and verifies.

1. Reproduce on the matching surface or build the smallest faithful reproducer. If unavailable, report the precise gap and do not claim a runtime pass.
2. Use evidence to eliminate hypotheses. Read relevant code and history rather than starting separate investigation agents by default.
3. Before choosing the fix, derive the [behavioral contract](../../../docs/verification.md#behavioral-contract) and its paired cases: the reproduction is one failing case, not the contract. Decide the [review](../../../docs/review.md) trigger.
4. Make the smallest fix that satisfies both paired outcomes. Add a regression test when it meaningfully captures the failure. A function boundary does not trigger architecture exploration.
5. Rerun the reproducer, both paired cases, affected checks, and repository-required verification. Review the diff under the [review policy](../../../docs/review.md). Reuse [evidence](../../../docs/verification.md) only while its inputs remain valid.

Escalate only under [efficiency](../../../docs/efficiency.md), for a named unresolved question; required independent review is not an escalation and is not waived by budgets. Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report root cause, fix, observed before/after behavior, and limits.
