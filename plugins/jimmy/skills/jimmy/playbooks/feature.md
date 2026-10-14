### Feature

**You own the design. Plan, review, verify.** Delegate implementation. Stay in the lead.

1. `how` over the affected subsystem.
2. Use `architect` when Jimmy's design trigger applies. Pass step 1's grounding into Phase A. For a routine change with an established shape, state that shape and proceed without a design arena.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Run each gate before the slices that depend on it. Unrelated ready slices can start in parallel.
   - **Independent workstreams.** Use **swarm** for independent, checkable slices. Start ready slices together. Separate shared write targets before serializing actual dependencies.
   - **Shared mutable state.** Default to splitting the target (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Delegate code-writing to a subagent using your configured feature role (default `agent_type: "worker-fast"`) with a specific scope (file paths, named data shape and its organizing structure per **principle-model-the-domain**, a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic, and success criteria). Use the **arena** skill when unresolved implementation alternatives have materially different behavior or ownership. Routine choices follow the chosen design without competing candidates. Split independent implementation slices through **swarm**. Keep one worker only when dependencies, shared ownership, or coordination cost make a split unhelpful. Reuse the architect decision rather than running a second arena for the same choice. Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved). A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation. No "standing by" reply that waits on a nested agent. Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it.
6. Rebase into small, ordered commits. Stack follow-ups.
   Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next.
7. If the design is contested, `interrogate` before shipping.
8. Run **Opening a PR**.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner proactively uses **swarm** as soon as independent slices are ready. Reassess at phase boundaries and when a dependency clears. Do not hold ready work behind an unrelated gate. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Reuse the owner for immediate corrections within the same scope. Use a fresh owner for new scope or an unusable report. Do not chain interrupts.

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.
