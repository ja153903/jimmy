# Jimmy

Jimmy builds Claude Code and Codex packages from a pinned pstack source. Shared workflow rules keep routine edits direct. Host adapters define the tools, models, and paths each runtime supports.

## Build and verify

```sh
python3 plugins/scripts/build.py
python3 -m unittest discover -s plugins/scripts -p 'test_*.py'
python3 plugins/scripts/build.py --check
```

## Install

Build first, then add this repository as a marketplace.

For Codex:

```sh
codex plugin marketplace add /absolute/path/to/jimmy
codex plugin add jimmy@jimmy
```

For Claude Code:

```text
/plugin marketplace add /absolute/path/to/jimmy
/plugin install jimmy@jimmy
```

Start a new chat after installing. Invoke `jimmy` in Codex or `/jimmy:jimmy` in Claude Code.

See the [plugin guide](plugins/README.md) for prerequisites, generated package paths, upstream preview and acceptance commands, and validation limits. The [evaluation procedure](plugins/docs/evaluation.md) covers workflow behavior, token spend, and elapsed time.

## Credit

Jimmy adapts [pstack by Lauren Tan](https://github.com/cursor/plugins/tree/main/pstack). Its MIT license is preserved in [plugins/jimmy/LICENSE](plugins/jimmy/LICENSE) and both generated packages.
