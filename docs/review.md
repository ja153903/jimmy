# Review policy

This is the authoritative review policy. Other skills and playbooks link here instead of restating the triggers.

## Lead review

The lead reviews every completed diff against the user's contract and the repository's required checks.

## Independent review triggers

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

Reviewers check the author's interpretation against the user's contract as well as checking the implementation. A correct implementation of a wrong interpretation is a finding.

## Records

Record in task state:

- the review trigger, or the concrete reason no trigger applies
- the reviewed input state (commit plus relevant staged, unstaged, and untracked files)
- findings
- disposition of each finding

If required independence is unavailable, report the missing review and do not claim review completion. Self-review does not substitute for required independent review.

## Count and rounds

Honor configured or explicitly requested reviewer counts. Otherwise use one independent reviewer and one round.

After fixes, recheck the changed scope and affected behavior. Repeat independent review when a fix introduces a new trigger or invalidates the earlier review, for example by changing the reviewed interpretation or the guarded logic itself.

Before completion or PR submission, confirm the recorded review input state matches the diff actually being delivered.
