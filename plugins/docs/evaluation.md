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
| Add a scoped feature across two files with established ownership. | One lead implements and verifies it. No default worker, design panel, or separate explainer. |
| Explain one module, then ask a follow-up about unchanged code. | The lead answers directly and reuses valid findings without spawning an explainer. |
| Ask why a known local decision exists. | The agent searches relevant history and linked evidence; it does not enumerate every connector by default. |
| Compare two interface choices. | The lead compares short sketches and implements once when authorized. Competing full builds require a stated reason. |
| Request an arena with two candidates. | Two isolated outputs, lead selection, no default extra judge, and verification of integrated output. |
| Request three independent reviewers. | The requested count overrides the default. Unsupported independence is disclosed. |
| Delegate two slices, then begin another phase. | Worker count is accounted for across the whole task. A third worker needs an unresolved question and stopping condition; budgets do not reset per phase. |
| Reuse a successful check before PR preparation. | No rerun solely for a phase change when inputs and required checks permit reuse. |
| Change an unstaged source file, test, lockfile, or relevant environment after a passing check. | The affected evidence is invalidated and relevant checks rerun. An unchanged commit SHA is insufficient. |
| Integrate two individually passing worker outputs. | The integrated artifact is verified. Isolated worker checks do not establish integration success. |
| Introduce a failure after the default review pass. | The agent diagnoses, repairs, and rechecks it; budgets do not excuse incomplete work. |
| Inspect a worktree with no supplied transcript location. | The agent reports missing chat evidence without inferring inactivity or reading Cursor history. |
| Request an unsupported cloud workflow. | The agent reports the missing capability and does not claim a local process provides equivalent execution. |

Check the actual file diff, checks, tool calls, and configuration writes. A statement that a skill was followed is insufficient evidence. A package that parses is not a behavioral pass.

## Compare cost and elapsed time

Run the original and adapted workflow on the same host, model, effort, fixture, and task. Restore the fixture between runs. Alternate the order and collect at least five successful runs per variant. Record CLI and model versions, cache state, machine load, concurrency, and the exact source commit.

Record host-reported input tokens, cached input tokens, output tokens, total tokens, elapsed time, tool calls, subagent calls, failures, and the verified task result. Include delegate usage when the host exposes it. If it does not, mark the token total incomplete. Do not infer token counts from characters or words, and do not report subscription dollars without supported billing evidence.

Reject failed or skipped work as evidence of improved performance. Compare medians and ranges. Investigate whether model generation, tool latency, repeated reads, or agent startup limits the result. A difference smaller than trial variation is inconclusive.

Keep raw host event output beside each result. Redact credentials and unrelated data. Report behavior and measurement gaps next to any claimed improvement.

## Record the execution path

For each trial, keep a compact record next to raw host events:

- Variant commit and built package version, host/model/effort, fixture state, task, trial number, and success or failure.
- Start/end times and elapsed time, with phase intervals when the host exposes them: grounding, implementation, delegation/startup, review, verification, and retries. Do not sum overlapping intervals as wall time.
- Host-reported input, cached input, output, and any separately reported reasoning tokens. Preserve the host's definitions; do not add reasoning tokens twice if they are included in output. Record lead and delegate usage separately and aggregate only when events establish whether parent totals already include children.
- Tool calls, agents launched, review rounds, duplicate implementations, failed attempts, checks reused, and reasons for escalation.
- Required artifact checks, observed results, and any missing usage or runtime evidence. Missing counts are null or unavailable, never zero.

Compare the current baseline to each change group as well as the final package: consistent default adapters, conditional delegation/design, then bounded context and verification reuse. Keep model and effort settings fixed to isolate routing changes. Evaluate cheaper models or lower effort in a separate comparison after the workflow comparison.

Judge time and tokens separately at equivalent verified outcomes. Include failed trials and repair work in the report, even though failed runs cannot count as successful speedup samples. Report success rate alongside successful-run medians and ranges so a fast but unreliable variant cannot win by dropping failures. Do not claim billing savings from raw token totals without applicable billing evidence.

Behavioral forward-tests can run in temporary fixture repositories with a compact independent agent brief. Give the evaluator the request, candidate skill, and raw fixture, without the expected answer or previous diagnosis. Inspect its actual edits and tool evidence. This is a routing check, not an end-to-end cost benchmark; fresh-host trials and host usage are still needed.
