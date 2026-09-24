# Jimmy plugin

Jimmy is a set of agent workflows for deliberate implementation, concise writing, and runtime verification. This package includes the Jimmy skill, its playbooks and scripts, its companion skills, and the `jimmy-agent` definition.

The package has manifests for Codex and Claude Code. Install this plugin through the marketplace at the repository root. Invoke `jimmy` to activate the workflow.

The original skill was written for Claude Code. Some playbooks still name Claude Code tools, model roles, and commands such as `/loop`. Codex can discover the skills through the Codex manifest, but those Claude-specific steps require adaptation to equivalent tools in the active environment. The prompt hook uses `CLAUDE_PLUGIN_ROOT` and only runs in a host that supports the Claude hook frontmatter.

The scripts under `skills/jimmy/scripts` include Bun and GitHub CLI based workflows. Install those tools before using the associated playbooks.

Selected workflows, playbooks, and principles are adapted from [pstack by Lauren Tan](https://github.com/cursor/plugins/tree/main/pstack). See [LICENSE.pstack](LICENSE.pstack) for the preserved MIT notice.

## Agents in Codex

The Markdown definitions in `agents/` are not loaded as Codex custom agents. Install converted TOML files in a project's `.codex/agents/` directory with:

```sh
python3 plugins/jimmy/scripts/install-codex-agents.py .codex/agents
```

For personal use across projects, pass `~/.codex/agents` as the destination. The script converts all nine roles, maps their model settings to Codex models, and marks review roles as read-only. Run it again after editing a Markdown source. Ask Codex to delegate a bounded task to a role by name, such as `worker-fast` or `critic-risk`.
