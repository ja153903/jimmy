### Refactoring

Preserve behavior while changing structure. The lead owns the change.

1. Identify the behavior contract and callers. Use existing coverage when it pins the contract; add a focused characterization check when coverage is missing and the move can change behavior.
2. Name the target structure and make the smallest useful move. Compare short designs only if ownership or interfaces are unresolved. Crossing a function boundary is not an escalation trigger.
3. Migrate affected callers and references. Delegate mechanical work only when independent ownership and saved elapsed time justify the shared [budget](../../../docs/efficiency.md).
4. Verify behavior, inspect the integrated diff, and complete required repository checks. Reuse valid [evidence](../../../docs/verification.md). Split new behavior or unrelated bug fixes from this change.

Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report the structural change, preserved behavior, checks and outcomes, and remaining limits.
