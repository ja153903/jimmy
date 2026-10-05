#!/usr/bin/env bash
# Read-only worktree prune audit. Classifies every git worktree by size, merge
# state, uncommitted work, remote/PR state, and the most recent chat that
# operated in it. Emits a table sorted by size with a suggested bucket. Never
# deletes anything; deletion stays a human-gated step in the playbook.
#
# Usage: worktree-audit.sh [repo-path]   (defaults to the current repo)
set -u

repo="${1:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$repo" ] && { echo "not in a git repo; pass a repo path" >&2; exit 1; }
cd "$repo" || exit 1

# Main worktree is the first entry; everything else is a candidate.
main_wt=$(git worktree list --porcelain | awk '/^worktree /{sub(/^worktree /, ""); print; exit}')

# origin/main drives the merge check. Best-effort; stale is fine for a first pass.
git fetch origin main --quiet 2>/dev/null || echo "warn: could not fetch origin/main; merged column may be stale" >&2

# PR state by branch, fetched once. Empty if gh is unavailable.
prs=$(mktemp)
sessions=$(mktemp)
trap 'rm -f "$prs" "$sessions"' EXIT
gh pr list --author "@me" --state all --limit 1000 \
	--json number,state,headRefName,headRefOid 2>/dev/null > "$prs" || echo "[]" > "$prs"

python3 - "$sessions" <<'PY'
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

root = Path(os.environ.get("JIMMY_SESSION_ROOT", os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
worktrees = [Path(line.removeprefix("worktree ")).resolve() for line in subprocess.check_output(["git", "worktree", "list", "--porcelain"], text=True).splitlines() if line.startswith("worktree ")]
mentions = [(str(path), re.compile(re.escape(str(path)) + r"(?=[/\s\"'`]|$)")) for path in worktrees[1:]]
usage = {}
for directory in ("sessions", "archived_sessions"):
    for path in (root / directory).rglob("*.jsonl"):
        try:
            modified = int(path.stat().st_mtime)
            with path.open() as stream:
                for line in stream:
                    try:
                        record = json.loads(line)
                        payload = record.get("payload", {})
                        cwd = payload.get("cwd") if record.get("type") in ("session_meta", "turn_context") else None
                        paths = [cwd]
                        if payload.get("type") == "function_call" and payload.get("name", "").split(".")[-1] == "exec_command":
                            arguments = json.loads(payload.get("arguments", "{}"))
                            paths.append(arguments.get("workdir"))
                        # Exec input is opaque code: count path mentions, never evaluate it.
                        if payload.get("type") == "custom_tool_call" and payload.get("name", "").split(".")[-1] == "exec":
                            code = payload.get("input")
                            if isinstance(code, str):
                                paths.extend(path for path, pattern in mentions if pattern.search(code))
                        try:
                            timestamp = int(datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00")).timestamp())
                        except (KeyError, ValueError, TypeError, AttributeError):
                            timestamp = modified
                        for cwd in paths:
                            if isinstance(cwd, str) and Path(cwd).is_absolute():
                                cwd = str(Path(cwd).resolve())
                                usage[cwd] = max(usage.get(cwd, 0), timestamp)
                    except (ValueError, TypeError, AttributeError):
                        continue
        except (OSError, ValueError, TypeError):
            continue
Path(sys.argv[1]).write_text(json.dumps(usage))
PY
now=$(date +%s)

printf "SIZE\tAGE\tMERGED\tDIRTY\tREMOTE\tPR\tLAST_CHAT\tBUCKET\tWORKTREE\n"

git worktree list --porcelain | awk '/^worktree /{sub(/^worktree /, ""); print}' | while read -r wt; do
	[ "$wt" = "$main_wt" ] && continue

	size=$(du -sh "$wt" 2>/dev/null | awk '{print $1}')
	head=$(git -C "$wt" rev-parse HEAD 2>/dev/null)
	head_ts=$(git -C "$wt" log -1 --format='%ct' HEAD 2>/dev/null || echo 0)
	age=$([ "$head_ts" -gt 0 ] 2>/dev/null && echo "$(( (now - head_ts) / 86400 ))d" || echo "?")

	# Squash-merged branches are not ancestors of main, so PR state is the
	# real signal; merge-base only catches fast-forward/rebase merges.
	git merge-base --is-ancestor "$head" origin/main 2>/dev/null && merged=YES || merged=no

	# Git cannot establish that an untracked file is disposable.
	porcelain=$(git -C "$wt" status --porcelain 2>/dev/null)
	if [ -z "$porcelain" ]; then dirty=clean
	elif printf '%s\n' "$porcelain" | grep -qv '^??'; then
		dirty="wip:$(printf '%s\n' "$porcelain" | grep -cv '^??')"
	else dirty="untracked:$(printf '%s\n' "$porcelain" | grep -c '^??')"; fi

	branch=$(git -C "$wt" symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
	if [ -z "$branch" ]; then remote=detached
	elif git -C "$wt" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
		[ "$(git -C "$wt" rev-parse "origin/$branch" 2>/dev/null)" = "$head" ] \
			&& remote=pushed \
			|| remote="ahead$(git -C "$wt" rev-list --count "origin/$branch..HEAD" 2>/dev/null)"
	else remote=no-remote; fi

	pr=$([ -n "$branch" ] && jq -r --arg b "$branch" \
		'.[] | select(.headRefName==$b) | "#\(.number)/\(.state)"' "$prs" 2>/dev/null | head -1)
	[ -z "$pr" ] && pr="-"
	pr_head=$([ -n "$branch" ] && jq -r --arg b "$branch" \
		'.[] | select(.headRefName==$b) | .headRefOid // empty' "$prs" 2>/dev/null | head -1)

	last="-"; last_ts=0
	last_ts=$(python3 - "$sessions" "$wt" <<'PY'
import json
from pathlib import Path
import sys
usage = json.loads(Path(sys.argv[1]).read_text())
worktree = Path(sys.argv[2]).resolve()
print(max((modified for cwd, modified in usage.items() if worktree == Path(cwd) or worktree in Path(cwd).parents), default=0))
PY
) || last_ts=0
	if [ "$last_ts" -gt 0 ]; then
		last=$(python3 - "$last_ts" <<'PY'
from datetime import datetime
import sys
print(datetime.fromtimestamp(int(sys.argv[1])).strftime("%Y-%m-%d"))
PY
)
	fi
	recent=$([ "$last_ts" -gt 0 ] 2>/dev/null && [ $(( (now - last_ts) / 86400 )) -le 4 ] && echo yes || echo no)

	case "$dirty" in wip:*) bucket=hold-wip ;; untracked:*) bucket=hold-untracked ;; *)
		case "$pr" in *OPEN*) bucket=hold-open-pr ;; *)
			if [ "$recent" = yes ]; then bucket=verify-recent-chat
			elif [ "$last_ts" -eq 0 ]; then bucket=review
			elif [ "$merged" = YES ]; then bucket=safe
			elif [[ "$pr" = */MERGED ]] && [ "$pr_head" = "$head" ]; then bucket=safe
			else bucket=review; fi ;;
		esac ;;
	esac

	printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
		"$size" "$age" "$merged" "$dirty" "$remote" "$pr" "$last" "$bucket" "$wt"
done | sort -t$'\t' -k1,1 -rh
