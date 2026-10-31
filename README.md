# Jimmy

A directory of coding skills shared by Claude Code and Codex. This repository is the package. Edit skills directly; no build step is required.

```text
skills/       Skills and their scripts, references, and assets
docs/         Shared workflow guidance
scripts/      Repository checks
```

Both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` point to `./skills/`. Both marketplace entries install this repository root.

## Install

Use the absolute path to this repository.

Codex:

```sh
codex plugin marketplace add /absolute/path/to/jimmy
codex plugin add jimmy@jimmy
```

Claude Code:

```text
/plugin marketplace add /absolute/path/to/jimmy
/plugin install jimmy@jimmy
```

Start a new chat after installation. Invoke `jimmy` in Codex or `/jimmy:jimmy` in Claude Code. If you installed from an old `plugins/dist/...` marketplace, replace that registration with the repository root. Keep one Jimmy installation per host.

## Use and maintain

Start with [Jimmy](skills/jimmy/SKILL.md). Read the [efficiency rules](docs/efficiency.md) for task-wide budgets and capability fallbacks, and the [delegate contract](docs/delegation.md) when delegating. The [guide](docs/guide/README.md) covers the collection.

Edit `skills/` and supporting resources directly. Instructions use the current session's available tools. Agent briefs do not register host roles. Model selection, history access, cloud execution, and scheduling depend on the host's actual capabilities.

Preserve invocation policy when editing: an explicit-only skill carries `disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Both metadata files coexist beside the same instructions.

## Verify

```sh
python3 scripts/check_package.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Package validation checks the maintained skills, manifests, invocation metadata, and local links without modifying files. Run affected helpers with their documented runtimes; fresh-host behavior checks follow [the evaluation procedure](docs/evaluation.md).

## Credit

Jimmy derives from [pstack by Lauren Tan](https://github.com/cursor/plugins/tree/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack), originally based on pstack 0.15.36 at commit `c742dd61706fbacc1b95f1a20b7b988cf096ce6c`. Its MIT license is preserved in [LICENSE](LICENSE).
