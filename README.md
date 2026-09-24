# Jimmy

Jimmy packages agent workflows for implementation, review, writing, and verification. This repository contains a Codex marketplace with one installable plugin.

## Install in Codex

Clone this repository, then run:

```sh
codex plugin marketplace add /absolute/path/to/jimmy
codex plugin add jimmy@jimmy
```

Start a new Codex task after installing so it loads the plugin. For a published GitHub repository, replace the local path with `owner/jimmy`.

## Contents

- `plugins/jimmy/skills` contains Jimmy and its companion skills.
- `plugins/jimmy/agents` contains Claude Code agent definitions.
- `plugins/jimmy/skills/jimmy/playbooks` and `scripts` contain the workflow material.

Jimmy was written for Claude Code. Some playbooks still refer to Claude Code tools, model roles, and commands such as `/loop`. Codex can discover the skills, but those steps need adaptation to the active host. The Claude prompt hook depends on `CLAUDE_PLUGIN_ROOT`.
