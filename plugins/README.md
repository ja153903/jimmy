# Jimmy

Jimmy builds Claude Code and Codex packages from a pinned pstack snapshot. The imported source under `jimmy/` uses Jimmy names. Local runtime and workflow changes live under `adapters/`.

## Build and check

Run these commands from the repository root. Python 3.9 or newer and Git are required. The updater uses POSIX file locking on macOS or Linux. Bundled pstack CLIs additionally require Bun. PR workflows need an available forge tool or configured CLI.

```sh
python3 plugins/scripts/upstream.py check
python3 plugins/scripts/build.py
python3 -m unittest discover -s plugins/scripts -p 'test_*.py'
python3 plugins/scripts/build.py --check
```

The generated packages are `plugins/dist/codex` and `plugins/dist/claude`. Edit the adapters and rebuild. The check command rejects source drift and stale generated files.

## Install locally

Build the packages first. Use absolute paths in the commands below.

For Codex, add the generated marketplace and install its plugin.

```sh
codex plugin marketplace add /absolute/path/to/jimmy/plugins/dist/codex
codex plugin add jimmy@jimmy
```

For a current Claude Code release with plugin support, run these commands inside Claude Code.

```text
/plugin marketplace add /absolute/path/to/jimmy/plugins/dist/claude
/plugin install jimmy@jimmy
```

Start a new chat after installation. Invoke `jimmy` in Codex or `/jimmy:jimmy` in Claude Code. Install only one Jimmy version in a host to avoid duplicate skill names.

Codex uses the agent types exposed by the session. Plugin Markdown agents are reference instructions, not proof that Codex registered custom roles. Claude Code can load its native plugin agents. Neither package needs Cursor installed.

## Update pstack

The lock records the upstream repository, commit, version, naming transform, normalized file hashes, and modes. It covers skills, agents, docs, the license, README, and source manifest. Cursor automations and root assets were absent from the supplied snapshot and are outside this import scope.

Create a separate preview from an upstream ref.

```sh
python3 plugins/scripts/upstream.py update --ref main --output /tmp/jimmy-update
```

The updater resolves the ref to a full commit, checks the current source against the lock, fetches the managed files, applies Jimmy naming, and builds both packages in the preview. Local adapters stay separate. It never overwrites this working copy.

Review the reported source changes and any adapter changes they require. Run the tests in the preview and try affected workflows in both hosts. Once reviewed, accept the preview. The command rebuilds against your current adapters, adopts source additions and deletions, and checks that the original pin has not changed.

```sh
python3 plugins/scripts/upstream.py accept --preview /tmp/jimmy-update
```

To retry the exact version, use the full commit from the preview lock instead of `main`.

This removes manual fork merging. It does not automate semantic review of new tools, workflow rules, or host behavior.

Acceptance keeps a journaled backup beside this directory until adoption succeeds. After an interrupted adoption, rerun the same accept command to restore the previous source and retry. Do not delete the backup while recovering.

## Control workflow cost

The `jimmy` entrypoint handles a routine, scoped change directly. It loads a playbook and relevant principles when the task warrants them. Crossing a function boundary alone does not start an architecture panel. Delegates receive focused briefs and reuse relevant context.

The shared efficiency policy also applies when a companion skill is invoked directly. Explicit requests for design exploration or independent review still take precedence. Host model choices default to inheritance, so the package does not pin unsupported or expensive model slugs.

These changes reduce mandatory instruction loading and agent fanout by construction. Actual token spend and elapsed time depend on the task and runtime. No speedup or cost saving has been measured. Use [the evaluation procedure](docs/evaluation.md) before claiming one.

## Source and adapters

- `jimmy/` and `.cursor-plugin/plugin.json` contain the imported pstack source with Jimmy naming.
- `upstream.lock.json` records the source commit, naming transform, and normalized resource hashes.
- `scripts/branding.py` renames upstream workflow identifiers and paths on every import while retaining Lauren Tan's attribution and license.
- `adapters/common/` contains Jimmy's shared routing policy and portable replacements.
- `adapters/codex/` and `adapters/claude/` define host capabilities and paths.
- `scripts/` builds, checks, and previews updates.
- `dist/` contains generated installation packages.

The upstream Cursor manifest remains only as provenance. The generated packages use native manifests and load their host runtime before following inherited workflow instructions. Advanced cloud execution, persistent orchestration, and recurring automations work only when the active host exposes the required capabilities. Unsupported steps must be reported.

Pstack is [Lauren Tan's MIT-licensed project](https://github.com/cursor/plugins/tree/09d06eb4b97a1020ab31e84030e38baf1099c7dc/pstack). Its license is preserved in `jimmy/LICENSE` and both generated packages. Native packaging follows the [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins) and [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference).
