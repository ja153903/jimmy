### Feature

The lead owns inspection, implementation, verification, and review.

1. Identify affected ownership, callers, acceptance criteria, and relevant data shape. Reuse existing grounding. When the plan adds or changes a guard or lifecycle behavior, derive the [behavioral contract](../../../docs/verification.md#behavioral-contract) and its paired cases first. Decide the [review](../../../docs/review.md) trigger. Read and apply [verification planning](../../../docs/verification.md#verification-planning) to choose checks for the affected journey.
2. Implement one solution. If an interface or ownership choice is consequential and unclear, compare short sketches through [architect](../../architect/SKILL.md) first.
3. Delegate only independent slices that justify their cost under [efficiency](../../../docs/efficiency.md); use [swarm](../../swarm/SKILL.md). Do not require a worker or arena for ordinary implementation choices.
4. Verify the actual behavior and required repository checks. Reuse valid [evidence](../../../docs/verification.md), review the integrated diff under the [review policy](../../../docs/review.md), and finish when acceptance criteria are covered.

Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report behavior changed, material decisions, checks and results, and remaining limits.
