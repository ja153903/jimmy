### Feature

The lead owns inspection, implementation, verification, and review.

1. Identify affected ownership, callers, acceptance criteria, and relevant data shape. Reuse existing grounding.
2. Implement one solution. If an interface or ownership choice is consequential and unclear, compare short sketches through [architect](../../architect/SKILL.md) first.
3. Delegate only independent slices that justify their cost under [efficiency](../../../docs/efficiency.md); use [swarm](../../swarm/SKILL.md). Do not require a worker or arena for ordinary implementation choices.
4. Verify the actual behavior and required repository checks. Reuse valid [evidence](../../../docs/verification.md), inspect the integrated diff, and finish when acceptance criteria are covered.

Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report behavior changed, material decisions, checks and results, and remaining limits.
