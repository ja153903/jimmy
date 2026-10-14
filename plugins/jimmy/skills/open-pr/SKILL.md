---
name: open-pr
description: Prepare a reviewed pull request title and body from the current branch, then open PR creation in the browser.
---

# Open a pull request

Resolve the repository's actual base branch and the current branch's intended target. Read `git diff <base>...HEAD`, commit messages, changed files, and the conversation. Inspect `git status` for uncommitted work. Commit only task-relevant changes; leave unrelated edits alone.

Write a title under 72 characters and a body that leads with the concrete problem and resulting behavior. Include the main changes and the checks actually run. Add a before/after example when it helps review. Use the repository's PR template when one exists. Read [technical-writing](../technical-writing/SKILL.md) for the description.

Save the final multiline body to a temporary file and inspect it before opening creation. Push the branch to its resolved remote if needed. When `gh` is the available PR route, run:

```bash
gh pr create --web --base "$PR_BASE" --title "$PR_TITLE" --body-file "$PR_BODY_FILE"
```

Set `PR_BASE`, `PR_TITLE`, and `PR_BODY_FILE` from the reviewed values before running the command. Keep untrusted title and body text out of the shell command itself.

The `--web` flag opens the creation form for the user to submit. After submission, verify the resulting PR's base, title, body, and readiness when the tool can read them. Attach the PR to the task with `mcp__codex_app__attach_artifact` when available. Use a direct PR creation tool only when the user asks for direct creation instead of browser submission.
