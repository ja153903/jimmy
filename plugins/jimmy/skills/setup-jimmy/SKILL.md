---
name: setup-jimmy
description: Configure Jimmy's per-role agents, models, and reasoning budget. Validate available Codex choices and write preferences that override skill defaults. Use for /setup-jimmy, "configure jimmy models", "jimmy budget", or changing Jimmy's model choices.
---

# Setup Jimmy

Write `~/.codex/jimmy-models.md` for account preferences. A project's `.codex/jimmy-models.md` takes precedence when present. Jimmy workflows read these files explicitly; Codex does not apply them as automatic rules. Configure the existing project file when present unless the user asks for account preferences. Otherwise use the account file.

## Steps

### 1. Detect available agents and models

Read the current subagent tool's exposed role names, model choices, and supported reasoning efforts. If Codex exposes a model listing, use it for additional available choices. Installed agent TOML files show configuration; they do not prove that the current session can spawn those roles.

Jimmy ships these role definitions:

| Role | Purpose | Writes |
|---|---|---|
| `worker-fast` | precisely specified implementation | yes |
| `worker-deep` | implementation needing judgment | yes |
| `critic-risk` | operational risk and failure modes | no |
| `critic-deep` | correctness and invariants | no |
| `critic-broad` | design and blast radius | no |
| `critic-fast` | mechanics and hygiene | no |
| `judge` | scoring and synthesis | no |
| `comment-sicko` | comment review | comments only |
| `jimmy-agent` | the full installed Jimmy workflow | yes |

Offer only roles and real model IDs confirmed available in this session. `inherit`, `inherit-parent`, and `auto` are always valid aliases. They use the parent chat model without a model override. If neither roles nor models can be detected, ask for the user's available choices. Do not guess model IDs.

### 2. Load current state

Read the account file, then the project file when present. A project line overrides the same account line; a missing line falls back to the account value, then the skill default. Show which file will receive this setup run's changes.

Read the current `# budget` line and role choices. Start missing roles from the defaults in step 5. Normalize a legacy `jimmy:` prefix to the exposed Codex role name when available. Keep valid overrides and panel lists. Drop role keys absent from step 5 and report each dropped key. Mark any unavailable role or model as needing a choice.

### 3. Budget, map, and confirm

Ask for a reasoning budget, naming the current budget when recorded. Use the available structured question tool when it supports this choice, or a concise numbered question. Offer these labels:

- `unlimited, keep max`
- `large, xhigh reasoning`
- `medium, high reasoning`
- `small, medium reasoning`

`unlimited` keeps each role's configured default effort. The other budgets target `xhigh`, `high`, or `medium`. Keep the selected role, model family, panel list, and aliases on a re-run. For a direct model choice, use its highest supported effort at or below the target. If there is no supported effort at or below it, mark the entry as needing a choice. Aliases keep the parent model and effort.

Fixed Codex roles carry their model and `model_reasoning_effort` in agent TOML. A Markdown budget line cannot override them, and the subagent tool may forbid overrides on a fixed role. To apply a budget to Jimmy's installed roles, use the plugin's converter on the intended agent directory:

```bash
python3 <jimmy-plugin-root>/scripts/install-codex-agents.py <agent-directory> --reasoning-effort high
```

Use `xhigh` for large, `high` for medium, and `medium` for small. Omit `--reasoning-effort` to restore source defaults for unlimited. The converter validates its supported model and effort combinations before writing. It updates Jimmy's role definitions and preserves their read-only restrictions. Explain which files it will replace. Respect the user's installation scope and existing permission boundaries. Custom role definitions need their own supported effort setting; do not rewrite unrelated agents.

The converter restores packaged model choices. If an installed role has a custom model, preserve it and update only its effort after validating that model's supported settings. Do not reinstall over custom model choices to change a budget.

Use a fresh Codex session when necessary to load changed agent definitions. Until the current tool advertises the chosen effort, report the budget as recorded but pending activation. For a direct model choice, pass its supported model and reasoning override through the available subagent API. Do not claim an override is active when the tool cannot apply it.

Show every role with its proposed agent or model and effective effort. Mark unavailable choices and budgets needing activation. Ask whether to accept the table or change specific roles, offering detected choices and aliases.

Panel roles take a comma-separated list. Each entry, including an alias, spawns one agent. Preserve distinct reviewer lenses in critique panels. Arena runners can repeat worker roles when comparing independent implementations. `arena cross-judge pool` is a list from which Arena selects one entry, preferring a model family different from the parent's when available. `swarm workers` supplies the default worker unless an arm has its own choice.

### 4. Validate

Validate each value against the detected roles and model IDs, or the aliases. Validate each requested effort against that model or the actual fixed role settings. Never write an unavailable real choice. Resolve invalid entries with the user. Retain pending activation only when the chosen budget can be installed and the user understands its current status.

### 5. Write the preferences

Overwrite the chosen file with validated preferences. Re-runs converge to the same content and remove retired role keys. For the account file, preserve the effective choices loaded in step 2. For a project file, preserve its existing explicit overrides and add only overrides the user selects. Do not copy inherited account values into project lines merely because they appeared in the effective table. Remove a project line when the user selects account fallback. Use exposed Codex role names, available model IDs, or aliases as values. The account defaults are:

```text
# Jimmy role configuration. Delete a line to fall back to the next preference file or skill default.
# inherit, inherit-parent, and auto use the parent model and effort.
# budget: unlimited (defaults)
feature, refactoring: worker-fast
bug-fix: worker-deep
perf-issue: worker-deep
hillclimb: worker-deep
judgment and prose: worker-deep
hardest tasks: worker-deep
how explorer: worker-fast
how explainer: worker-deep
how critics: critic-risk, critic-deep, critic-broad, critic-fast
why investigators: worker-fast
why synthesizer: judge
reflect tooling: critic-fast
reflect judgment: critic-deep
reflect divergent: critic-broad
reflect synthesizer: judge
arena runners: worker-deep, worker-fast, worker-deep, worker-fast
arena cross-judge pool: judge, critic-deep
swarm workers: worker-fast
architect runners: critic-risk, critic-deep, critic-broad, critic-fast
interrogate reviewers: critic-risk, critic-deep, critic-broad, critic-fast
```

Replace the budget line with the selected budget and actual target, for example `# budget: medium (high)`. Read back the written file and check all entries. A missing preference file leaves workflow defaults in effect.

### 6. Confirm

Tell the user which preference file changed, which retired keys were removed, and whether the reasoning budget is active or awaits updated agent definitions in a fresh session. Preferences apply when a workflow next reads them. Re-running setup updates them.

### 7. Offer a verification skill, optional

Check for a project-local `verify-*` skill or an existing harness that drives the real app. If none exists, offer once to create one with `create-verification-skill`. Resolve that skill from the available skills list. Proceed only if the user accepts. If they decline, finish without pushing.
