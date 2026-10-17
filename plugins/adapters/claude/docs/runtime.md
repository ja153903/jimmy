# Jimmy in Claude Code

This file controls Claude Code behavior wherever inherited pstack files name Cursor tools, paths, models, or permissions. The current tool schema is authoritative. A skill cannot grant a missing tool or expand the user's authorization.

Find this package from the `skills/jimmy/SKILL.md` path you loaded. Do not assume a plugin-root environment variable. Project skills live in `.claude/skills/`; personal skills live in `~/.claude/skills/`. Plugin agents may appear as `jimmy:jimmy-agent` and `jimmy:comment-sicko` when Claude Code registers them. Check the actual agent list before invoking either. Otherwise use an exposed `general-purpose` agent with the role lens in the brief.

Use Claude Code's `Agent` tool only when exposed. Follow its supported fields for model, effort, isolation, background work, and resume. Do not translate Cursor's `Task`, `run_in_background`, cloud environment, or worktree fields by guess. Give each writing agent exclusive files or an actual isolated checkout. If agents are unavailable, own the work directly and report any lost independent review. Ask the user through a native question tool when available, or plain text when it is absent.

Read project `.claude/jimmy-models.md` and then account `~/.claude/jimmy-models.md` once per workflow context. A project role line wins; an absent line falls back to the account file. The default is `inherit-parent`. These files are explicit Jimmy preferences, not automatically loaded rules. Use only model aliases and reasoning levels the current tool accepts. Do not reuse Cursor's Grok, Fable, speed, or `xhigh` examples unless the current schema confirms them.

Claude Code has no pstack mode sentinel. Do not run `jimmy-mode.on`, `jimmy-mode-on`, Cursor hooks, or inherited mode rules. Keep the selected workflow in this task's context. Retrieve prior context only from the exact named task through a tool that exposes it or from a path supplied by the user or runtime. Do not infer a transcript path or read a guessed newest session.

Run the repo's real verification command or use an available terminal, browser, app, or service tool. Use an exposed recurring task or automation tool only when the user authorizes recurring work. A sleeping shell is not a future audit. Use a native PR tool when it supports the action, otherwise a usable forge CLI. Cursor cloud agents, review bots, and automations have no claimed Claude Code equivalent without a real tool.

For skill authoring, use a skill creator only when available. Otherwise edit the `SKILL.md` and validate its frontmatter and links. External messages and irreversible operations still require authorization from this task.
