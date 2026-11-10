# Workflow fixtures

Executable fixtures for forward-testing Jimmy's review and verification workflow in Claude Code and Codex. They follow the [evaluation procedure](../../docs/evaluation.md).

Each fixture has:

- `given/`: the project the evaluating agent receives.
- `request.txt`: the only instruction the evaluating agent receives.
- `hidden/`: acceptance checker, rubric, and reference variants. Never copy it into the evaluator's workspace or brief.

## Run a trial

1. Copy `given/` to a fresh temporary directory outside this repository and run `git init && git add -A && git commit -m fixture` there.
2. Start a fresh host session in that directory with Jimmy installed. Send the contents of `request.txt` and nothing else.
3. Retain the raw tool record: the host's event log or transcript, including delegate events. Redact credentials.
4. Run `node hidden/acceptance.mjs <trial-dir>` from the fixture directory.
5. Grade every row of `hidden/rubric.md` against the checkout and the tool record.

Acceptance passing is not a workflow pass. Review, contract derivation, and verification are graded only from the tool record.

## Fixtures

- [Session identity](session-identity/hidden/rubric.md): a retry guard keyed on session identity instead of operation identity.
- [Existing app](existing-app/hidden/rubric.md): a CLI without journey verification gains a `list` command; the workflow must create, execute, and clean up a project verification skill.

`scripts/test_workflow_fixtures.py` checks that each acceptance checker rejects the original and known-bad variants and accepts the reference.
