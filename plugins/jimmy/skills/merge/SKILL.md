---
name: merge
description: Commit and merge a workmux-managed worktree into its observed local target branch.
---

# Merge a workmux worktree

Use this skill for a local workmux merge. For a pull request or stack that must land on the remote, follow Jimmy's [Shipping playbook](../jimmy/playbooks/shipping.md).

Read the user's invocation text for `--keep` (`-k`) or `--no-verify` (`-n`). Pass only requested flags to `workmux merge`. `--keep` preserves the worktree after merging; `--no-verify` skips pre-merge hooks.

1. Confirm the current checkout is a workmux-managed worktree. Inspect `git status`, the current branch, and the target. Read `branch.<current>.workmux-base` from local Git config. If it is absent, resolve the configured workmux main branch from the repository; do not guess `main`. Stop if the target remains ambiguous or does not exist locally.
2. Review the diff and run the checks required for this change. Commit staged changes with a lowercase imperative message and no conventional prefix. Leave unrelated or unstaged changes untouched. Workmux will refuse a merge while uncommitted changes remain.
3. Run `workmux merge --rebase --into <observed-target> --notification`, adding `--keep` or `--no-verify` only when requested. Specifying `--into` matters for worktrees based on another feature branch because workmux otherwise merges into its configured main branch. The `--rebase` flag performs the rebase; do not rebase a second time first.
4. If the rebase stops on a conflict, inspect the target's recent changes to each conflicting file with `git log -p -n 3 <target> -- <file>`. Resolve the conflict without dropping either branch's intended behavior, stage the file, and run `git rebase --continue`. Then finish the workmux merge and verify the target contains the intended commit.

Do not use `--no-verify` unless the user requested it. Do not merge a branch with an unresolved check or conflict.
