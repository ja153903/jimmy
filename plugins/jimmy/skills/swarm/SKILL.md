---
name: swarm
description: "Fan out parallel workers and return one report. Use for /swarm, races, coverage, or discovered independent work in implementation, exploration, verification, and review."
---

# Swarm

Fan out N parallel workers. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

Use swarm proactively whenever implementation, exploration, verification, or review reveals independent, checkable slices, even when the user did not name swarm. Reassess when dependencies clear. Start ready slices together and give each worker exclusive outputs. Separate shared write targets first. Serialize only real dependencies or writes that must remain shared. Slice coverage does not require competing solutions; race workers only when comparing independent solutions is useful.

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is the total worker count. Launch waves when it exceeds the available concurrency slots.
4. Pick the worker from the `swarm workers` configuration line, default `worker-fast`. Resolve runtime and model preferences per [the Codex runtime reference](../jimmy/references/codex-runtime.md). Reuse the current workflow context in nested skills. Project values take precedence. Missing role lines keep the defaults below. `inherit` and `auto` select an override-capable generic agent with the role lens in its prompt and no model or reasoning override, as the runtime reference specifies. For a model race, name each arm's available model up front.
5. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Spawn workers with `collaboration.spawn_agent` and the step 4 role as `agent_type`. Launch in waves within the available concurrency limit. Each brief names its owned files or outputs and says other writers are present. Use separate directories or managed worktrees when workers need independent repository states.

When a worker must start from a non-default branch, prepare its checkout explicitly and pass its absolute path. A spawn does not create or switch worktrees.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

Track retries per lane across the whole run. If a worker drops out or returns no usable result, retry that lane once with a fresh worker and a consolidated brief. After a second miss, record a gap.

## Phase C: Aggregate

Read the terminal results. A result missing the SHAs or method its brief names is unusable. Apply the same one-retry limit from Phase B. After the retry is spent, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
