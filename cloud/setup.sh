#!/bin/bash
# Claude Code cloud environment setup script. Paste into the environment's
# "Setup script" field on claude.ai. Fails loudly (non-zero exit blocks the
# session from starting) so a broken install is noticed instead of sessions
# silently running without the stack.
set -euo pipefail

STACK_DIR=/opt/agent-stack

git clone --depth 1 https://github.com/joecirillo/agent-stack.git "$STACK_DIR"

mkdir -p ~/.claude
cp "$STACK_DIR/instructions/AGENTS.md" ~/.claude/CLAUDE.md

claude plugin marketplace add "$STACK_DIR"
claude plugin install agent-stack@agent-stack
