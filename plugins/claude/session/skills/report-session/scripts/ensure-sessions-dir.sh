#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${CLAUDE_PROJECT_DIR:-}" && -d "$CLAUDE_PROJECT_DIR" ]]; then
  root="$CLAUDE_PROJECT_DIR"
elif root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  root="$(pwd)"
fi

dir="$root/.claude/sessions"
mkdir -p "$dir"
printf '%s' "$dir"
