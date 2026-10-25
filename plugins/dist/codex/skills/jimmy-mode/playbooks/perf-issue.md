### Perf issue

Tie the change to measurement. The lead owns the baseline, implementation, and comparison.

1. Capture the actual slow path and baseline. Use [benchmark checklist](../../benchmark-checklist/SKILL.md) before acting on or reporting measured differences.
2. Find the limiter. Prefer removing unnecessary work, reusing valid work, and reducing frequency before concurrency or a cheaper implementation.
3. Implement one hypothesis at a time and verify outputs as well as timing. Delegate only independent experiments within the shared [budget](../../../docs/efficiency.md). A function boundary does not require an architecture panel.
4. Compare equivalent runs, including failures and retries. Report inconclusive results when measurement cannot support a difference. Keep the raw evidence.

Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report the measurement, method, limiter, verified behavior, and limitations. Sustained optimization can use [hillclimb](hillclimb.md), retaining task-wide budgets.
