### Autonomous run

Define a checkable finish condition, permitted actions, verification commands, and a durable record path before the first iteration. Apply the task-wide [efficiency budget](../../../docs/efficiency.md).

1. Work toward the finish condition in small verifiable units. Each iteration makes the smallest change supported by evidence and runs the relevant checks before starting the next unit. Inspect the diff; preserve unrelated work and discard only your own unsuccessful changes. Commit checkpoints when within the user's scope.
2. Keep a compact record of what changed, verification commands and observed results, current state of the finish condition, remaining decisions, and the next action. Use [Show me your work](../../show-me-your-work/SKILL.md) when a fuller decision log is useful.
3. Address discoveries within the authorized goal. Record unrelated follow-ups separately. Resolve reversible implementation choices with evidence; surface missing product decisions, access, or authorization when they prevent progress. Do not relax the finish condition to claim success.
4. Follow active work with native status or wait tools. If continuation requires a later wakeup, use an exposed scheduling tool only when the user authorized recurring work. Without one, complete the active session's work and report the exact continuation gap and next action. A prompt or sleeping shell does not provide unattended execution.
5. Stop when the finish condition passes, the user stops the work, or progress requires unavailable input or a capability. Diagnose failed checks and replan from evidence instead of repeating an unchanged attempt.

Report the finish condition and its final state, completed work, verification evidence, remaining limits, and the record path needed to resume.
