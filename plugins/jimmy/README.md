# Jimmy plugin

Jimmy is a set of agent workflows for deliberate implementation, concise writing, and runtime verification. This package includes the Jimmy skill, its playbooks and scripts, its companion skills, and the `jimmy-agent` definition.

The package has manifests for Codex and Claude Code. Install this plugin through the marketplace at the repository root. Invoke `jimmy` to activate the workflow.

The shared workflows track pstack 0.15.9 at commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. All 50 upstream skills and their supporting resources have counterparts, and Jimmy retains its 14 additional skills. The [Codex runtime adapter](skills/jimmy/references/codex-runtime.md) maps upstream agents, model preferences, chat history, control skills, and scheduled audits to the tools available in the current session.

The scripts under `skills/jimmy/scripts` use Bun, GitHub CLI, and Git. Install their dependencies with `bun install --frozen-lockfile` from that directory. The orchestration store's frontier command also requires Graphite. The PR watcher supports GitHub base-branch stacks without Graphite.

New upstream skills include `correct`, `benchmark-checklist`, and `principle-explain-the-number`. The port also includes `principle-attack-the-premise` and `principle-test-behavior-not-implementation`, which were absent from the earlier import.

Selected workflows, playbooks, and principles are adapted from [pstack by Lauren Tan](https://github.com/cursor/plugins/tree/main/pstack). See [LICENSE.pstack](LICENSE.pstack) for the preserved MIT notice.

## Agents in Codex

The Markdown definitions in `agents/` are not loaded as Codex custom agents. Install converted TOML files in a project's `.codex/agents/` directory with:

```sh
python3 plugins/jimmy/scripts/install-codex-agents.py .codex/agents
```

For personal use across projects, pass `~/.codex/agents` as the destination. The script converts all nine roles and preserves their Codex model, reasoning effort, and read-only settings. Run it again after editing a Markdown source. Ask Codex to delegate a bounded task to a role by name, such as `worker-fast` or `critic-risk`.

To apply a reasoning budget to the installed roles, pass `--reasoning-effort medium`, `high`, or `xhigh`. Omit the option to restore the source defaults. The installer validates all roles before writing and leaves identical files untouched. Start a fresh Codex session when needed to load the changed definitions. `setup-jimmy` records role preferences in `~/.codex/jimmy-models.md`, with per-line project overrides in `.codex/jimmy-models.md`.

## Verify upstream coverage

Run `python3 scripts/check-pstack-parity.py` from this plugin directory. Add `--source /path/to/pstack` to verify the source snapshot too. The [inventory](pstack-upstream.json) pins every shared resource and records the reviewed local hashes. After reviewing a future port, refresh it with:

```sh
python3 scripts/check-pstack-parity.py --record --source /path/to/pstack --version <version> --commit <full-commit-hash>
```

Recording hashes does not prove semantic parity or authenticate the supplied commit. Obtain the source from that commit, review the upstream diff and Codex adaptations, then run the affected tools before recording a new snapshot.
