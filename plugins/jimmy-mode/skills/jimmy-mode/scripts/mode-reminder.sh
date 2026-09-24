#!/usr/bin/env bash
# Re-injects the mode reminder while the mode is active.
# Active means ${CLAUDE_PROJECT_DIR}/.claude/jimmy-mode.state exists.
set -uo pipefail
state="${CLAUDE_PROJECT_DIR:-.}/.claude/jimmy-mode.state"
[[ -f "$state" ]] || exit 0
echo "New task? Playbook match or rigor needed -> apply /jimmy-mode. Casual turn or user opts out -> don't."
