# Jimmy

Jimmy ports pstack's engineering workflows to Codex. This repository contains a Codex marketplace with one installable plugin.

## Install in Codex

Clone this repository, then run:

```sh
codex plugin marketplace add /absolute/path/to/jimmy
codex plugin add jimmy@jimmy
```

Start a new Codex task after installing so it loads the plugin. For a published GitHub repository, replace the local path with `owner/jimmy`.

## Contents

- `plugins/jimmy/skills` contains Jimmy and its companion skills.
- `plugins/jimmy/agents` contains role definitions and an installer for Codex custom agents.
- `plugins/jimmy/skills/jimmy/playbooks` and `scripts` contain the workflow material.

The port covers all 50 skills in pstack 0.15.9, pinned to commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, plus 14 Jimmy-specific skills. Existing skills, playbooks, references, and supporting scripts are included. Codex tools replace the upstream host's agent calls, model rules, transcript paths, and recurring audit commands. See the [runtime adapter](plugins/jimmy/skills/jimmy/references/codex-runtime.md).

The [upstream inventory](plugins/jimmy/pstack-upstream.json) records the source and reviewed port hashes. Check resource coverage, frontmatter, links, and drift with:

```sh
python3 plugins/jimmy/scripts/check-pstack-parity.py
```

Pass `--source /path/to/pstack` to also compare an extracted upstream snapshot. Hash checks detect changes since review; they do not prove workflow behavior. See the [plugin README](plugins/jimmy/README.md) for tool and agent setup.

## Credit

Selected workflows, playbooks, and principles are adapted from [pstack by Lauren Tan](https://github.com/cursor/plugins/tree/main/pstack). The original work is MIT licensed. Its copyright and permission notice are preserved in [plugins/jimmy/LICENSE.pstack](plugins/jimmy/LICENSE.pstack).
