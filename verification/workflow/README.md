# Workflow fixtures

Executable fixtures for forward-testing Jimmy's review and verification workflow in Claude Code and Codex. They follow the [evaluation procedure](../../docs/evaluation.md).

Each fixture has:

- `given/`: the project the evaluating agent receives.
- `request.txt`: the only instruction the evaluating agent receives.
- `hidden/`: acceptance checker, rubric, and reference variants. Never copy it into the evaluator's workspace or brief.

## Run a trial

`uv run scripts/run_fixture.py <fixture> --host claude|codex`, or `--cmd '<any agent CLI> {prompt}'` for another provider, automates steps 1–4. The host runs in `{trial}`; `{package}` is a copy of Jimmy without fixture answers. The runner writes `result.json`, raw host output, `diff.patch`, and the trial's [evidence records](../../docs/verification.md#evidence-cli), and flags host output that mentions hidden material. From the records it grades: contract recorded before any edit (and whether it has paired cases), a passing receipt at the delivered tree that reproduces when the runner reruns it, and the delivery gate’s review result (`covered`, `missing`, `reported-missing`, or `not-required`). Rows the records cannot show, such as the formal-verification assessment, are still graded by hand from host output. The built-in `claude` template uses `bypassPermissions` in the throwaway trial directory; the `codex` template uses Codex's installed Jimmy and its workspace-write sandbox.

Manual steps:

1. Copy `given/` to a fresh temporary directory outside this repository and run `git init && git add -A && git commit -m fixture` there.
2. Start a fresh host session in that directory with Jimmy installed. Send the contents of `request.txt` and nothing else.
3. Retain the raw tool record: the host's event log or transcript, including delegate events. Redact credentials.
4. Run `node hidden/acceptance.mjs <trial-dir>` from the fixture directory.
5. Grade every row of `hidden/rubric.md` against the checkout and the tool record.

Acceptance passing is not a workflow pass. Use evidence records and the raw tool log to grade the workflow.

## Fixtures

- [Session identity](session-identity/hidden/rubric.md): a retry guard keyed on session identity instead of operation identity.
- [Existing app](existing-app/hidden/rubric.md): a CLI without journey verification gains a `list` command; the workflow must create, execute, and clean up a project verification skill.

`scripts/test_workflow_fixtures.py` checks that each acceptance checker rejects the original and known-bad variants and accepts the reference.
