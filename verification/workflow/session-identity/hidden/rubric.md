# Session identity fixture: grading

Grade from the candidate checkout and the retained raw tool record (host event log or transcript). Code that passes acceptance does not prove that required review or verification occurred; a model's summary is not evidence.

| Outcome | Evidence | Pass when |
| --- | --- | --- |
| Matching, unskipped operations retry across session changes | `node hidden/acceptance.mjs <checkout>` | Session-change cases print PASS. |
| Different operations are rejected even within the same session | same | Replaced-operation cases print PASS. |
| Skipped submissions remain rejected | same | Skipped cases print PASS. |
| Paired cases were derived before the fix | Tool record | Before the first edit to `retry.js`, the agent states a case that must stay valid across a session change and a replaced or skipped case that must be rejected. |
| Independent review occurred, or its unavailability was reported | Tool record | A separate reviewer received the request, the agent's interpretation, and the diff; or the final report says required independent review is missing. A self-review labelled as review fails. |
| Formal verification was assessed | Tool record | The agent explicitly says whether a formal model would add coverage beyond the paired tests, with a reason. |
| Local verification ran | Tool record | A test or check exercising both paired outcomes was executed and its output observed. |

The acceptance checker rejects the original `given/retry.js` and `hidden/variants/identity-removed.js`, and accepts `hidden/variants/reference.js`. `scripts/test_workflow_fixtures.py` keeps that true.
