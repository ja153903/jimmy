### Bug fix

The lead reproduces the defect, identifies its mechanism, implements, and verifies.

1. Reproduce on the matching surface or build the smallest faithful reproducer. If unavailable, report the precise gap and do not claim a runtime pass.
2. Use evidence to eliminate hypotheses. Read relevant code and history rather than starting separate investigation agents by default.
3. Make the smallest justified fix. Add a regression test when it meaningfully captures the failure. A function boundary does not trigger architecture exploration.
4. Rerun the reproducer, affected checks, and repository-required verification. Inspect the diff. Reuse [evidence](../../../docs/verification.md) only while its inputs remain valid.

Escalate only under [efficiency](../../../docs/efficiency.md), for a named unresolved question or independent review risk. Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report root cause, fix, observed before/after behavior, and limits.
