# Jimmy plugin

Jimmy is a set of agent workflows for deliberate implementation, concise writing, and runtime verification. This package includes the Jimmy skill, its playbooks and scripts, its companion skills, and the `jimmy-agent` definition.

The package has manifests for Codex and Claude Code. Install this plugin through the marketplace at the repository root. Invoke `jimmy` to activate the workflow.

The original skill was written for Claude Code. Some playbooks still name Claude Code tools, model roles, and commands such as `/loop`. Codex can discover the skills through the Codex manifest, but those Claude-specific steps require adaptation to equivalent tools in the active environment. The prompt hook uses `CLAUDE_PLUGIN_ROOT` and only runs in a host that supports the Claude hook frontmatter.

The scripts under `skills/jimmy/scripts` include Bun and GitHub CLI based workflows. Install those tools before using the associated playbooks.
