### Orchestrate

Use this for a standing program that outlives one task. For work the lead can finish in one session, use [Autonomous run](autonomous-run.md). Apply the task-wide [efficiency budget](../../../docs/efficiency.md); a program does not automatically authorize a fleet or nested coordinators.

Name the finish condition, work units, dependencies, permitted actions, and evidence required for each unit. Start with one unit through implementation and verification before expanding a novel workflow. Use the [delegate contract](../../../docs/delegation.md) and the current host's agent tools. One owner writes each branch or PR; the owner handles its fixes and rebases. Assign separate checkouts to concurrent writers. The lead coordinates and inspects artifacts, and can implement directly when delegation is unavailable or would add cost without resolving an independent slice.

Keep a compact durable record at a user-specified path or a task-local file outside the source tree: unit, owner, branch or PR, dependencies, current head SHA, verification commands and results, next action, and unresolved decisions. Update it when these facts change. Use exposed plan or project storage tools when available; otherwise use the durable record without building a replacement bookkeeping service. Include only the relevant established facts and dependency results in each fresh brief.

Inspect the actual diff or artifact before accepting a unit. Verification covers its recorded input state, per [verification evidence](../../../docs/verification.md). A new push requires checking what changed and rerunning affected checks; green CI and worker summaries alone are insufficient. Use independent review for a named risk or an explicit request, within the remaining review budget. Report missing independence when the host cannot provide it.

Use native wait or status tools to follow active agents, and an available forge tool or CLI to check a PR's live head and checks before reporting or landing it. Message a worker for follow-up work, not as a status probe. Future wakeups require an authorized native automation tool. Without one, finish the active session and leave the exact next action in the record; do not promise unattended continuation.

Retry according to evidence: narrow scope after a context limit, retry a transient connection failure, or change an unsupported tool choice. After two unsuccessful retries for the same unit, record the blocker and replan around it. Reconcile late results with the current branch before using them. Account for every started unit as completed, replaced, or blocked. Keep discoveries outside the goal as follow-ups. Publishing and merging remain within the user's authorization.

Report progress against the finish condition, each PR's live state and verification scope, unresolved decisions, and the durable record path. At handoff, name the next command or action needed to resume.
