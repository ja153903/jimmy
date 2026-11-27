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

Acceptance passing is not a workflow pass. Use evidence records and the raw tool log to grade the workflow. The runner's review field reports the CLI's mechanical trigger floor. Independently check the raw tool record against the broader [review policy](../../docs/review.md), including review for every observable behavior change. A `not-required` artifact field cannot waive that policy.

## Fixtures

- [Session identity](session-identity/hidden/rubric.md): a retry guard keyed on session identity instead of operation identity.
- [Existing app](existing-app/hidden/rubric.md): a CLI without journey verification gains a `list` command; the workflow must create, execute, and clean up a project verification skill.

- [Deferred completion ownership](async-ownership/hidden/rubric.md): queued provider callbacks retain operation ownership through session changes, cancellation, and late outcomes.
- [Privacy-preserving review repairs](review-privacy/hidden/rubric.md): an automated logging request must retain customer-content exclusion, cancellation, and fallback behavior.
- [Real configuration consumer](consumer-contract/hidden/rubric.md): the existing operator CLI must consume both prompts and their individual criteria.

The three historical cases adapt synthetic projects from [figma/jimmy](https://github.com/figma/jimmy/tree/1a941381334cf8683a4e0814fc759baf0e873852/verification/engineering). They use the same runner, host templates, evidence grading, and hidden-material exclusion as the existing cases. Run, for example:

```sh
uv run scripts/run_fixture.py async-ownership --host claude
uv run scripts/run_fixture.py consumer-contract --host codex
```

The Codex template uses the installed Jimmy. Confirm that the candidate package is loaded before grading a live trial. Fixture self-checks establish grader behavior, not agent success rates or performance improvements.

Run `uv run python -m unittest discover -s scripts -p 'test_*fixtures.py'` to check all five fixtures. `scripts/test_workflow_fixtures.py` covers the original two; `scripts/test_historical_fixtures.py` covers the three historical cases. These checks reject original and known-bad implementations, accept reference repairs, preserve protected artifacts, and verify that hidden material is withheld. Historical acceptance requires both public tests and private checks. Each runs in a separate disposable copy of the delivered project, so public test setup cannot repair the state inspected by private checks or change the delivered checkout. These copies isolate fixture state, not adversarial code or operating-system access.
