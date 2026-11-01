#!/bin/bash
# SessionStart hook (compact matcher): after context compaction, surface
# what was in progress so the agent can pick up where it left off.
set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')
cd "$CWD" 2>/dev/null || exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

CHANGED=$(git status --porcelain 2>/dev/null)
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null)

if [ -z "$CHANGED" ] && [ -z "$RECENT_COMMITS" ]; then
  exit 0
fi

echo "Context recap after compaction (from \`git status\`/\`git log\` in ${CWD}):"

if [ -n "$CHANGED" ]; then
  echo ""
  echo "Uncommitted changes:"
  echo "$CHANGED"
fi

if [ -n "$RECENT_COMMITS" ]; then
  echo ""
  echo "Recent commits:"
  echo "$RECENT_COMMITS"
fi
