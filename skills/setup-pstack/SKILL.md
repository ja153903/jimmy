---
name: setup-pstack
description: Configure optional per-role Jimmy model preferences for the current host when the user asks to choose models or budgets.
---

Read [efficiency](../../docs/efficiency.md) once per workflow context for task-wide budgets and available capabilities.

# Set up pstack models

Use the current session's exposed delegation schema to check available model and reasoning options. Use an existing, explicitly configured Jimmy preference file or a destination the user names. If no destination is configured, ask for it before writing. Preferences are read explicitly by Jimmy and do not configure the host itself.

Use the project file for this repository or the account file for the user's default, according to the request. Read the current file first. Keep the role labels already used by its workflows, including `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `judgment and prose`, `hardest tasks`, `how explorer`, `how explainer`, `why investigators`, `why synthesizer`, `swarm workers`, `arena runners`, `arena cross-judge pool`, `architect runners`, and `interrogate reviewers`. Drop a retired role only after checking its callers.

Default each unconfigured role to `inherit-parent`. Treat `auto` as the same alias. Do not infer a model slug, family, effort level, or speed suffix from another host's example. List models and reasoning levels from the actual agent tool or another authoritative runtime source. Write only an override that this session can run. If availability cannot be checked, leave that role inherited and state the limit.

For a requested budget, map it only to reasoning levels that the tool exposes. Show the user the resulting choices when their preference is unclear. Write a simple `role: model` line for a single role or comma-separated values for a panel. Preserve unrelated valid lines. Read the file back and check every configured value against the current tool schema. Tell the user which path was written and when a new agent will read it.
