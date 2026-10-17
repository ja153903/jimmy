# Evaluate workflow behavior and cost

Build and validate both generated packages before running this procedure. Run it in temporary fixture repositories. Keep real accounts, messages, production systems, and unrelated projects out of the fixtures.

## Verify behavior first

Use the same fixture and request in both hosts. Start a fresh chat for each trial.

| Request | Required result |
| --- | --- |
| Change a known README typo. | The file changes correctly. The agent uses a focused check and does not start a design panel. |
| Fix a function that mishandles an empty collection. | The defect is reproduced and the relevant behavior passes after the fix. |
| Configure Jimmy model preferences. | The host reads its own preference file. No Cursor configuration is created. |
| Design a change with two viable ownership choices. | The agent compares the choices and verifies the chosen design. |
| Request two independent read-only reviewers. | The agent uses available native tools or explicitly reports that independent review is unavailable. |
| Inspect a worktree with no supplied transcript location. | The agent reports missing chat evidence without inferring inactivity or reading Cursor history. |
| Request an unsupported cloud workflow. | The agent reports the missing capability and does not claim a local process provides equivalent execution. |

Check the actual file diff, checks, tool calls, and configuration writes. A statement that a skill was followed is insufficient evidence. A package that parses is not a behavioral pass.

## Compare cost and elapsed time

Run the original and adapted workflow on the same host, model, effort, fixture, and task. Restore the fixture between runs. Alternate the order and collect at least five successful runs per variant. Record CLI and model versions, cache state, machine load, concurrency, and the exact source commit.

Record host-reported input tokens, cached input tokens, output tokens, total tokens, elapsed time, tool calls, subagent calls, failures, and the verified task result. Include delegate usage when the host exposes it. If it does not, mark the token total incomplete. Do not infer token counts from characters or words, and do not report subscription dollars without supported billing evidence.

Reject failed or skipped work as evidence of improved performance. Compare medians and ranges. Investigate whether model generation, tool latency, repeated reads, or agent startup limits the result. A difference smaller than trial variation is inconclusive.

Keep raw host event output beside each result. Redact credentials and unrelated data. Report behavior and measurement gaps next to any claimed improvement.
