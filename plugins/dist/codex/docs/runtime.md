# Jimmy in Codex

This file controls Codex behavior wherever inherited pstack files name Cursor tools, paths, models, or permissions. The tool schema exposed in this task is authoritative. A skill cannot grant a missing tool or expand the user's authorization.

Find this package from the `skills/jimmy/SKILL.md` path you loaded. Do not assume a plugin-root environment variable. Project skills live in `.agents/skills/`; personal skills live in `~/.agents/skills/`. Resolve installed plugin skills from the available catalog. The Markdown files in `agents/` are reference prompts. Their presence does not register a Codex agent role.

Use `collaboration.spawn_agent` only when exposed. Choose a supported role from its current schema and preserve the intended reviewer or worker lens in the brief. If delegation is unavailable, own the work directly and report any lost independent review. A shared checkout is not isolated. Give agents exclusive files or actual worktrees. Use the current tool's wait and message methods, without inventing `Task`, cloud, resume, or background fields. Use native question, plan, terminal, browser, app, and PR tools only when present.

Read project `.codex/jimmy-models.md` and then account `~/.codex/jimmy-models.md` once per workflow context. A project role line wins; an absent line falls back to the account file. The default is `inherit-parent`. Apply a model or reasoning override only through a tool and agent type that accept it. Check the current schema before using configured values. Fixed roles may ignore an override. Do not carry Cursor's model table into Codex.

Codex has no pstack mode sentinel. Do not run `jimmy-mode.on`, `jimmy-mode-on`, Cursor hooks, or inherited mode rules. Keep the selected workflow in this task's context. Retrieve prior context only through an exposed thread tool for the exact named task or a user-supplied transcript path. Do not search guessed transcript directories or select a newest session.

Use the repo's real verification command or an available terminal, browser, simulator, or app tool. If the user authorizes recurring audits and a native automation tool exists, use its supported schedule. A sleeping shell is not a future audit. Use a native PR tool when it supports the operation, otherwise a usable forge CLI. Verify the PR state and attach it when an attachment tool is exposed. Unsupported Cursor cloud, review-bot, and automation features remain unavailable unless an actual Codex tool provides the action.

For skill authoring, use the bundled skill creator if it appears in the catalog. Otherwise edit the `SKILL.md` directly and validate its frontmatter and links. External messages and irreversible operations still require authorization from this task.
