# Run work while you sleep

An unattended run needs a finish condition that a tool can check, permission boundaries, and a record of decisions. The host must also support a process or scheduled task that will keep running. Read [the host runtime](../runtime.md) for the tools available in Codex or Claude Code. A promise in a prompt does not keep a closed session alive.

## Set a checkable finish condition

Name the starting branch, permitted writes, verification command, and stop condition. For example:

```text
Use Jimmy to migrate every caller to the new parser in an isolated worktree.
Finish when no old callers remain, all parser fixtures pass, and the old API is deleted.
Commit reversible checkpoints and keep a decision log.
Stop and report if the checks cannot pass or a required tool is unavailable.
```

Use the [autonomous run playbook](../../skills/jimmy-mode/playbooks/autonomous-run.md) for one task. A large migration may first need [figure-it-out](../../skills/figure-it-out/SKILL.md). A queue of independent changes may need [Autopilot-stack](../../skills/jimmy-mode/playbooks/autopilot-stack.md). Use [Orchestrate](../../skills/jimmy-mode/playbooks/orchestrate.md) only for a standing program that outlives one task. Check each playbook's Cursor examples against the host runtime before acting.

For each change, run the real check and record the result. [Show me your work](../../skills/show-me-your-work/SKILL.md) describes the decision log. An agent can summarize that log when you return. Treat transcript access as available only when the exact task or path is supplied by the user or an exposed tool.

## Schedule only through an available tool

For later wakeups, use an actual recurring task or automation tool that the host exposes and the user has authorized. If the tool is absent, finish the current session's work and report that future runs cannot be armed. Do not use a sleeping shell process as a substitute.

The upstream pstack guide describes a Cursor `/loop` command, cloud agents, and a Benny automation pack. This package does not install that automation pack or claim those capabilities in Codex or Claude Code. Use a native exposed tool for equivalent work when one exists.

A duration is not a finish condition. Ask for a result that can pass or fail, such as a test suite and an old-call-site count.

Next: [Steer with principle names](./08-principles.md).
