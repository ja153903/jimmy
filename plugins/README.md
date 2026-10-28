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

The current pin is pstack 0.15.36 (`c742dd61706fbacc1b95f1a20b7b988cf096ce6c`). It includes PR-watcher deadline and fork-stack fixes, formal-verification creation and maintenance skills, and TLA+ statecharts. Jimmy's review adapter asks for executable reproductions and lead reruns while preserving unresolved risks that cannot be reproduced. It retains the task-wide reviewer budget. The orchestration adapter uses exposed host tools and a compact durable record instead of Cursor project storage or the removed `orch` CLI.

Formal verification is optional, for a named property that tests cover poorly. Generated project skills belong in the active host's project skill directory. Statechart needs a supported TypeScript runtime (see its launcher), plus TLC and Java 11 or later via `TLA2TOOLS` and `JAVA`, or mise for the pinned automatic installation. Initial downloads need network access. A renderer is optional; the model-checking result and Mermaid output remain usable without one. Verification must demonstrate that a broken variant fails, record its bounds and covered code, and distinguish model drift from product defects.

Integration validation: 25 Python packaging/updater tests, 61 PR-watcher/plan-check tests, and the watcher type check passed. A focused statechart run on Node 26.12.0 passed 192 tests, skipped one live fuzz check, and failed one diagnostic assertion: importing a view that throws `null` prints a Node-internal stack before the caught value. The same output occurs in a standalone dynamic import; statechart still exits 2 and writes no artifacts. Two additional live TLC fixture checks (Counter and MediaPlayer), using TLC 1.7.4 and Java 20, passed. Rendering, the full live fuzz suite, and automatic mise installation were not exercised. On macOS, run symlink tests with a canonical `TMPDIR`, and run process-cleanup tests where child-process inspection is permitted.

Acceptance keeps a journaled backup beside this directory until adoption succeeds. After an interrupted adoption, rerun the same accept command to restore the previous source and retry. Do not delete the backup while recovering.

## Control workflow cost

The default path is one lead inspecting, implementing one solution, verifying, and reviewing the diff. Shared adapters replace the routine playbooks and the `how`, `why`, `architect`, `swarm`, `arena`, and `interrogate` entrypoints. The imported source remains pinned for updates and reference. Default routing no longer depends on overriding contradictory instructions in those entrypoints.

[Efficiency](adapters/common/docs/efficiency.md) defines task-wide defaults: zero delegates, one implementation, and one review pass. A named uncertainty can justify two workers total or one independent reviewer. Design choices start with short sketches; arenas are reserved for uncertainty that warrants duplicate implementation or explicit requests. User-requested panel sizes and repository-required checks take precedence. These are instructions, not enforced host quotas. A budget increase requires a reason and stopping condition, not a new permission gate.

[Delegate briefs](adapters/common/docs/delegation.md) avoid full-chat inheritance when supported. Workers do not restart the parent's workflow or delegate recursively by default. Host model preferences are read when a delegate is needed, and otherwise add no startup step. [Verification evidence](adapters/common/docs/verification.md) can be reused across phases only while its relevant inputs remain unchanged, including dirty files and runtime dependencies. Integrated output still needs verification.

No speedup or cost saving has been measured. Use [the evaluation procedure](docs/evaluation.md) to compare behavior, elapsed time, total tokens including delegates, and failed attempts. Parallelism may reduce latency while increasing tokens.

## Source and adapters

- `jimmy/` and `.cursor-plugin/plugin.json` contain the imported pstack source with Jimmy naming.
- `upstream.lock.json` records the source commit, naming transform, and normalized resource hashes.
- `scripts/branding.py` renames upstream workflow identifiers and paths on every import while retaining Lauren Tan's attribution and license.
- `adapters/common/` contains Jimmy's shared routing policy and portable replacements.
- `adapters/codex/` and `adapters/claude/` define host capabilities and paths.
- `scripts/` builds, checks, and previews updates.
- `dist/` contains generated installation packages.

The upstream Cursor manifest remains only as provenance. The generated packages use native manifests and load their host runtime before following inherited workflow instructions. Advanced cloud execution, persistent orchestration, and recurring automations work only when the active host exposes the required capabilities. Unsupported steps must be reported.

Pstack is [Lauren Tan's MIT-licensed project](https://github.com/cursor/plugins/tree/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack). Its license is preserved in `jimmy/LICENSE` and both generated packages. Native packaging follows the [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins) and [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference).
