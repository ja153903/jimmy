# Jimmy-only skill audit

The pinned upstream is pstack 0.15.23 at commit `837067b75aa20ab58d7b2a2f6c0531e37118c596`. The [upstream record](../pstack-upstream.json) maps the copied pstack resources. `python3 scripts/check-pstack-parity.py --list-local-skills` lists the 14 skills below and no others. "Jimmy-only" describes provenance, not a recommendation to remove a skill.

All 14 remain. Several overlap a pstack playbook, but their requested behavior is distinct. The workmux skills manage local worktrees, `open-pr` prepares browser submission, and `hatch-pet` packages Codex pets. The three new upstream skills, `ketchup`, `in-your-own-words`, and `poteto-help`, do not replace any of these workflows.

| Skill | Disposition | Audit result |
| --- | --- | --- |
| `caveman` | Keep, narrow | Preserved the compressed voice and clarity exception. Removed an unsupported token-saving claim and made ordinary "be brief" requests reply-scoped. |
| `codebase-design` | Keep, repair | Its module vocabulary is a local design convention. `DESIGN-IT-TWICE.md` now names Codex's `collaboration.spawn_agent` and gives a direct fallback when delegation is unavailable. |
| `coordinator` | Keep, repair | This remains an optional workmux workflow. It now checks for a Codex pane, passes `-a codex`, avoids a race while waiting for `working`, reviews before merging, and specifies each merge target with `--into`. Cross-project messaging requires task scope. |
| `creating-course-lectures` | Keep, narrow | Preserved the course exercise and CodeGroup rules. It asks only about unresolved consequential choices, honors a course's existing practice format, and verifies problem metadata. |
| `domain-modeling` | Keep, narrow | Preserved glossary and ADR conventions. It now follows a repository's existing locations and creates documentation only when the task includes maintaining it. |
| `grill-me` | Keep, repair | Explicit interview alias now links to the local `grilling` skill instead of assuming a slash-command dispatcher. |
| `grill-with-docs` | Keep, repair | Explicit alias now links to `grilling` and `domain-modeling`. |
| `grilling` | Keep, narrow | It resolves observable questions from code or a cheap prototype and stops when the remaining design choices are settled. |
| `handoff` | Keep, repair | The temporary handoff workflow is distinct from pstack's in-chat session pickup. Removed unsupported Claude frontmatter. |
| `hatch-pet` | Keep, repair | The Codex v2 pet pipeline remains distinct from pstack. The script path now derives from the loaded plugin skill instead of assuming a personal skill installation. |
| `improve-codebase-architecture` | Keep, repair | The visual report and design interview remain local. Skill links now resolve to files. The HTML reference now states that Tailwind and Mermaid load from CDNs and requires readable offline findings. |
| `merge` | Keep, repair | This is a local workmux merge, separate from pstack's remote Shipping playbook. It now names the observed target with `--into` and avoids a second rebase. |
| `open-pr` | Keep, repair | Preserved browser submission. It prepares the body in a file, commits only task-related changes, uses the observed base, and attaches a submitted PR when available. |
| `rebase` | Keep, repair | Removed `$ARGUMENTS` and the `main` assumption. It resolves the saved workmux base or the requested local or remote target before rebasing. |

Eight skills had Claude-only `disable-model-invocation` frontmatter that Codex's bundled validator rejects. They now use `agents/openai.yaml` with `allow_implicit_invocation: false`, preserving explicit invocation. `allowed-tools` and `argument-hint` were removed where they described the old host rather than available Codex tools.

## Evidence

- `python3 scripts/check-pstack-parity.py --list-local-skills` returned exactly the 14 table names, with exit 0.
- The bundled `quick_validate.py` returned `Skill is valid!` for all 14 entrypoints. A local PyYAML-capable Python at `/Users/jaimeabbariao/.local/share/nvim/mason/packages/cmakelang/venv/bin/python` ran the validator.
- A Markdown link check outside fenced examples found 24 local links across these skills and reported `all local links resolve`. Eight `openai.yaml` policy files parsed with `allow_implicit_invocation: false`.
- `python3 -m unittest discover -s plugins/jimmy/skills/hatch-pet/tests -v` with the Codex bundled Python ran 24 tests and ended `OK`. Pillow emitted `Image.getdata` deprecation warnings; no test failed.
- `git diff --check` on the assigned skill directories returned exit 0 with no output.
- Installed `workmux 0.1.222` reports `-a, --agent` in `workmux add --help`. `workmux add --dry-run -a codex audit-dry-run` showed the intended worktree and exited 0. `workmux merge --help` reports `--into`, `--rebase`, `--keep`, and `--no-verify`. Its configuration reference says the default agent is `claude`, and its docs say a project without an agent pane or `CLAUDE.md` opens a shell by default. This checkout has no `.workmux.yaml`, `.workmux.yml`, or `CLAUDE.md`, so the coordinator's Codex-pane gate selects the runtime fallback here.

The audit did not launch workmux agents, merge branches, open a PR, generate images, or package a live pet. Those operations would require a task that invokes the respective skill. The structural checks and pet tests establish that the edited instructions and existing pet scripts are internally consistent; they do not prove those external workflows end to end.
