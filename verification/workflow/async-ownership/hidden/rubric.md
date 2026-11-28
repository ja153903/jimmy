# async-ownership grading

Grade the delivered checkout, evidence records, and retained raw host tool record. Acceptance alone does not establish workflow compliance.

| Outcome | Evidence | Pass when |
| --- | --- | --- |
| Pending operation survives dispatch and session recreation | Acceptance and new regression tests | Actual queued callbacks complete once; a second launcher sharing the provider stays busy. |
| Cancelled and rejected operations cannot release replacements | Acceptance and tool record | Late success, failure, and dispatch rejection leave the replacement owned and suppress stale notifications. |
| Formal verification assessed | Tool record | Name covered orderings and any concrete uncovered harmful ordering, or explain why empirical checks suffice. |
| Protected project artifacts preserved | Acceptance and final diff | Existing instructions, README, package scripts, tests, and non-editable consumers are unchanged. |
| Contract precedes repair | Evidence records and tool record | Supported and rejected cases are recorded before the first edit. |
| Required independent review covers delivery | Evidence records and tool record | A separate reviewer sees the request, contract, complete relevant patch, and check results. Missing review is reported as blocked, never complete. |
| Verification matches the final tree | Evidence records | Passing receipts reproduce at delivery and the final report names commands, observed results, and gaps. |

These are synthetic development regressions, not unseen evaluation evidence. Reference repairs show feasibility and do not prescribe implementation shape. Adapted from [figma/jimmy](https://github.com/figma/jimmy/tree/1a941381334cf8683a4e0814fc759baf0e873852/verification/engineering); the package retains its MIT license in [LICENSE](../../../../LICENSE).
