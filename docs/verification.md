# Verification evidence

Keep a short task-local record when a check will be reused across workers or phases. No persistent database or committed log is needed for an ordinary task.

Record the exact command, working directory, observed result, input state, and scope it covers. Input state includes the commit plus relevant staged, unstaged, and untracked files. A commit SHA alone does not identify a dirty checkout. Include relevant test files, configuration, lockfiles, generated artifacts, tool versions, and environment or service state when the check depends on them. Do not record secrets.

Reuse a successful check only when these inputs are unchanged and its scope covers the current acceptance criterion. For a small task, direct inspection of changes since the check is sufficient. If dependencies or input state are unclear, rerun the check. Never treat a timestamp, agent assertion, or prior success on a different checkout as proof.

Invalidate evidence when code, tests, dependencies, configuration, or relevant runtime state changes. Changes outside a proven dependency scope need not invalidate a focused check. Repository-required final checks still apply; do not replace them with a narrower check. A previously failed check needs fresh passing evidence after repair.

After merging worker outputs or grafting arena candidates, verify the integrated artifact. Isolated candidate checks do not cover integration. An external UI or live service check can become stale without a file change; reobserve it when current state matters.

The final answer names the checks and their observed outcome. Report a missing runtime check as a limit, not a pass. Stop when the required checks and material risks are covered; add another check only for a changed input, a failure, or a named uncovered risk.
