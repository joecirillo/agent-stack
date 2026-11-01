#!/bin/bash
# PreToolUse guard for `git push` Bash calls. Denies pushing directly to the
# repo's trunk branch regardless of how the push is phrased (bare `git push`
# while checked out on the trunk counts too, since branch name isn't always
# in the command string). Resolves the actual default branch via `gh` since
# not every repo's trunk is named main/master; falls back to those two names
# if `gh` can't resolve it (no remote, offline, not a GitHub repo, gh not
# authenticated).
#
# `timeout`/`gtimeout` aren't available on stock macOS and this repo doesn't
# want a new dependency just for this, so the 3s bound on the `gh` lookup is
# done manually: background it, race a killer against it, and use whatever
# it managed to print before either finishing or getting killed.
set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // "."')

cd "$CWD" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

BRANCH=$(git branch --show-current 2>/dev/null || echo "")
[ -n "$BRANCH" ] || exit 0

resolve_default_branch() {
  local outfile
  outfile=$(mktemp)
  gh repo view --json defaultBranchRef -q .defaultBranchRef.name >"$outfile" 2>/dev/null &
  local pid=$!
  (sleep 3; kill -9 "$pid" 2>/dev/null) &
  local watcher=$!
  wait "$pid" 2>/dev/null
  kill "$watcher" 2>/dev/null
  wait "$watcher" 2>/dev/null
  cat "$outfile" 2>/dev/null
  rm -f "$outfile"
}

DEFAULT_BRANCH=$(resolve_default_branch)

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ] || { [ -n "$DEFAULT_BRANCH" ] && [ "$BRANCH" = "$DEFAULT_BRANCH" ]; }; then
  jq -n --arg branch "$BRANCH" '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": ("Refusing to push directly to \($branch). Open a PR from a feature branch instead.")
    }
  }'
  exit 0
fi

exit 0
