---
name: setup-jimmy
description: Configure which role agent each jimmy role uses. Writes a config file that overrides the skill defaults. Use for /setup-jimmy, "configure jimmy models", or changing jimmy's model choices.
---

# Setup

Write `~/.claude/jimmy-models.md`, a config file that sets the role agent used
for each role. The skills read it when present and fall back to their inline
defaults when a line is absent, so this is an override layer, not a requirement.

## Steps

### 1. Show the available roles

Role agents ship with the plugin and carry a fixed model and effort level. There
is nothing to detect — the set is:

| Role agent | Model | Effort | Writes | Lens |
|---|---|---|---|---|
| `jimmy:critic-risk` | fable | max | no | operational risk, failure modes |
| `jimmy:critic-deep` | opus | max | no | correctness, invariants |
| `jimmy:critic-broad` | opus | xhigh | no | design, blast radius |
| `jimmy:critic-fast` | sonnet | high | no | mechanics, hygiene |
| `jimmy:judge` | fable | max | no | scoring candidates against a rubric |
| `jimmy:worker-fast` | sonnet | high | yes | precisely specified implementation |
| `jimmy:worker-deep` | fable | max | yes | implementation needing judgment |

`inherit` is also valid for any role and means the role runs on the parent
session's model with no subagent model override.

### 2. Load current state

The default role mapping is the file shape shown in step 4. If
`~/.claude/jimmy-models.md` already exists, read it and treat its values as the
current choices. Otherwise start from those defaults.

### 3. Map and confirm

Show every role with its current value. Ask whether to accept as-is or change
specific roles, offering the role agents above plus `inherit`. Prefer
`AskUserQuestion` over free text.

Panel roles (`how critics`, `arena runners`, `architect runners`,
`interrogate reviewers`) take a list, and one subagent runs per entry, so the
list length sets the fan-out. Keep the entries distinct: the panel's value comes
from four different lenses, and listing the same role agent four times produces
four near-identical reviews at four times the cost. If the user wants a larger
panel, repeat a role only after all four critics are already in the list.

`arena cross-judge pool` is also a list; Arena selects one entry from it.
`swarm workers` is the default for every worker unless a race assigns another
role per arm.

### 4. Write the config

Write `~/.claude/jimmy-models.md`, overwriting the whole file so re-runs stay
idempotent. Shape:

```
# jimmy role configuration. One line per role.
# Delete a line to fall back to the skill default.
# `inherit` means the role runs on the parent session's model.
feature, refactoring: jimmy:worker-fast
bug-fix: jimmy:worker-deep
perf-issue: jimmy:worker-deep
hillclimb: jimmy:worker-deep
judgment and prose: jimmy:worker-deep
hardest tasks: jimmy:worker-deep
how explorer: jimmy:worker-fast
how explainer: jimmy:worker-deep
how critics: jimmy:critic-risk, jimmy:critic-deep, jimmy:critic-broad, jimmy:critic-fast
why investigators: jimmy:worker-fast
why synthesizer: jimmy:judge
reflect tooling: jimmy:critic-fast
reflect judgment: jimmy:critic-deep
reflect divergent: jimmy:critic-broad
reflect synthesizer: jimmy:judge
arena runners: jimmy:worker-deep, jimmy:worker-fast, jimmy:worker-deep, jimmy:worker-fast
arena cross-judge pool: jimmy:judge, jimmy:critic-deep
swarm workers: jimmy:worker-fast
architect runners: jimmy:critic-risk, jimmy:critic-deep, jimmy:critic-broad, jimmy:critic-fast
interrogate reviewers: jimmy:critic-risk, jimmy:critic-deep, jimmy:critic-broad, jimmy:critic-fast
```

### 5. Confirm

Tell the user the config was written and that skills pick it up on their next
run. Re-running this skill updates it.

### 6. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a
`verify-*` skill, or an existing harness). If not, offer once: "want a
project-local verification skill, so agents can drive the app the way a user
does and prove changes work? I can generate one with
`/create-verification-skill`." On yes, invoke `/create-verification-skill`. On
no, move on without pushing.
