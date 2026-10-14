---
name: rebase
description: Rebase the current branch onto its saved workmux base, a named local branch, or an explicitly requested remote branch.
---

# Rebase the current branch

Read the requested target from the user's invocation text.

- With no target, use the current workmux worktree's saved base through `workmux rebase` when available. Otherwise inspect `branch.<current>.workmux-base` and the repository's local default branch. Do not assume the default branch is named `main`; stop if no target can be resolved.
- With a local branch name, rebase onto that branch without fetching.
- With a remote name alone, such as `origin`, fetch that remote and resolve its default branch from its HEAD. Do not assume `origin/main`.
- With `remote/branch`, fetch that remote and rebase onto the named remote-tracking branch.

Check `git status` before starting. Preserve uncommitted work by resolving it before the rebase. Do not silently discard or stash it.

For a workmux default-base rebase, run `workmux rebase`. For other targets, run `git fetch <remote>` only when the request names a remote, then `git rebase <resolved-target>`.

If conflicts occur, inspect the target's recent changes to each conflicting file with `git log -p -n 3 <target> -- <file>`. Resolve the intended behavior from both branches, stage the file, and run `git rebase --continue` until complete. Verify the resulting branch diff against the target.
