# Jimmy Mode

Jimmy Mode packages agent workflows for implementation, review, writing, and verification. This repository contains a Codex marketplace with one installable plugin.

## Install in Codex

Clone this repository, then run:

```sh
codex plugin marketplace add /absolute/path/to/jimmy-mode
codex plugin add jimmy-mode@jimmy-mode
```

Start a new Codex task after installing so it loads the plugin. For a published GitHub repository, replace the local path with `owner/jimmy-mode`.

## Contents

- `plugins/jimmy-mode/skills` contains Jimmy Mode and its companion skills.
- `plugins/jimmy-mode/agents` contains Claude Code agent definitions.
- `plugins/jimmy-mode/skills/jimmy-mode/playbooks` and `scripts` contain the workflow material.

Jimmy Mode was written for Claude Code. Some playbooks still refer to Claude Code tools, model roles, and commands such as `/loop`. Codex can discover the skills, but those steps need adaptation to the active host. The Claude prompt hook depends on `CLAUDE_PLUGIN_ROOT`.
