# Review policy

This is the authoritative review policy. Other skills and playbooks link here instead of restating the triggers.

## Lead review

The lead reviews every completed diff against the user's contract and the repository's required checks. Use [PR review](../skills/pr-review/SKILL.md) for requested reviews and the lead's final implementation review. It supplies inspection and reporting guidance; this policy remains authoritative for independent review and delivery.

## Independent review triggers

Require independent review for any implementation that changes observable behavior, including local-only tasks. Judge the diff and its callers, including changes to defaults, configuration, instructions that govern agent behavior, and refactors that could change runtime behavior.

Independent review is required when the diff changes logic or event ordering that governs any of:

- retries
- operation or session identity
- ownership
- cancellation
- permissions
- migrations
- shared mutable state

This includes intended behavior-preserving refactors of that logic or ordering. The trigger is the observable change in the code; the implementer does not need to identify a specific defect or risk first.

Documentation, formatting, and symbol-only renames do not trigger independent review by topic alone. An explicit user request or a repository requirement also triggers independent review.

Use [interrogate](../skills/interrogate/SKILL.md) to run it.

## Reviewer input

Reviewers receive:

- the original user request
- relevant documented behavior
- the author's interpretation of the request (the behavioral contract)
- the surrounding lifecycle of the changed code
- the complete relevant diff
- observed verification results for the reviewed tree, including the commands, outcomes, and coverage gaps

Reviewers check the author's interpretation against the user's contract as well as checking the implementation. A correct implementation of a wrong interpretation is a finding.

After the repository checks pass, focus independent review on what those checks could have missed. Ask for the affected caller or input, the failure mechanism, and the expected and observed behavior. Include the reproducer when practical. Treat an established repository convention as actionable when the reviewer can cite it. Fix confirmed findings and rerun affected checks. Keep unresolved material risks visible in the delivery report.

## Records

Record in task state:

- the review trigger, or the concrete reason no trigger applies
- the reviewed input state (commit plus relevant staged, unstaged, and untracked files)
- findings
- disposition of each finding

Record reviews with the [evidence CLI](verification.md#evidence-cli), which stores the reviewed tree with each record:

- `evidence.py review --request TEXT --cmd '<reviewer CLI reading stdin>'` (or `$JIMMY_REVIEWER`) runs a reviewer from any provider on an isolated checkout of the exact tree and records its output.
- For a host-native reviewer agent, save `evidence.py brief --request TEXT > /tmp/jimmy-brief.md` (use a unique path outside the checkout for concurrent reviews), give that file to the reviewer, then record its findings with `evidence.py review --findings FILE --by NAME --brief /tmp/jimmy-brief.md`. The record binds to that exact brief, so it covers only the diff that reviewer was shown. Give each reviewer its own `--by` name.
- With neither available, `evidence.py review --request TEXT` records the missing review.

Use the pre-change revision or tree as the review base for local work and the PR merge base for PR delivery. Pass the same `--base` to the brief or reviewer and to the delivery gate when using it. Reviewers end with `VERDICT: PASS` or `VERDICT: ISSUES`; `evidence.py gate` accepts only passing verdicts that saw the triggered changes, with no outstanding ISSUES.

Pass the verification summary through `--context` for both local and PR review. If the brief lists omitted files relevant to the review, have the reviewer inspect their complete patches against the same base in the isolated checkout before recording the verdict. Confirm this coverage in the review record. Apply the full review policy alongside the CLI's keyword floor.

If required independence is unavailable, report the missing review and do not claim review completion. Self-review does not substitute for required independent review.

## Count and rounds

Honor configured or explicitly requested reviewer counts. Otherwise use one independent reviewer and one round.

After fixes, recheck the changed scope and affected behavior. Repeat independent review when a fix introduces a new trigger or invalidates the earlier review, for example by changing the reviewed interpretation or the guarded logic itself.

## Delivery

Before reporting implementation work as complete, pushing commits, or publishing a PR, verify the actual diff against the behavioral contract and required repository checks. When independent review is required, confirm a passing review covers that diff and its confirmed findings are resolved. Reuse valid evidence across local handoff and PR preparation. Recheck affected behavior and renew review coverage after changes that invalidate it.

Run the applicable pre-publication checks locally or in an isolated environment. Check forge-only CI once the outgoing diff has been published and require it for merge readiness.

If a required check or review fails or is missing, or confirmed findings remain unresolved, keep the work local and report the blocker and the evidence you have. For a PR already open, keep the new changes local until they meet the same requirements.

## Recurring PR findings

Use actual PR review comments when available. Confirm the finding against the diff and repository conventions, then look for the same cause across comparable changes. Encode recurring mechanical findings in lint or type checks, behavior failures in regression tests, and repository conventions in the instructions read before editing. Prefer extending an existing check or instruction.

Compare actionable findings per comparable PR and regressions found after merge before and after a workflow change. Deduplicate findings by cause and use the same observation window and reviewer setup when practical. Report when the available sample is too small to judge the effect.
