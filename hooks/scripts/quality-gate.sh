#!/bin/bash
# Stop hook: if there are uncommitted changes in a recognized project, run
# its build/lint commands and block completion if any fail. Tests are
# deliberately excluded -- they can be slow/network-dependent (e.g. DB
# integration tests) and Stop fires after every response, not just at task
# completion, so a flaky or slow test suite blocked unrelated turns. Skips
# entirely when nothing changed. All failures are collected into a single
# decision block -- emitting one JSON object per failing check would break
# the hook's JSON parsing, which expects exactly one object on stdout.
set -uo pipefail

INPUT=$(cat)
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

CWD=$(echo "$INPUT" | jq -r '.cwd // "."')
cd "$CWD" 2>/dev/null || exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
[ -n "$(git status --porcelain 2>/dev/null)" ] || exit 0

FAILURES=""

record_failure() {
  local label="$1"
  local output="$2"
  FAILURES="${FAILURES}${label} failed:
$(echo "$output" | tail -n 40)

"
}

run_check() {
  local label="$1"
  shift
  local output
  output=$("$@" 2>&1)
  if [ $? -ne 0 ]; then
    record_failure "$label" "$output"
  fi
}

if [ -f package.json ]; then
  if [ -f pnpm-lock.yaml ]; then
    PM="pnpm"
  elif [ -f yarn.lock ]; then
    PM="yarn"
  else
    PM="npm"
  fi

  for script in build lint; do
    if jq -e --arg s "$script" '.scripts[$s]' package.json >/dev/null 2>&1; then
      run_check "$PM run $script" "$PM" run "$script"
    fi
  done
elif [ -f pom.xml ]; then
  run_check "mvn compile" mvn -q compile
elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
  run_check "gradle build" ./gradlew build -q -x test
fi

if [ -n "$FAILURES" ]; then
  jq -n --arg reason "$FAILURES" '{"decision":"block","reason":$reason}'
fi

exit 0
