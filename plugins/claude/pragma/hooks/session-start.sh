#!/usr/bin/env bash
# SessionStart hook — emits instructions.md as session context.
#
# Claude Code reads hookSpecificOutput.additionalContext. jq --rawfile does the
# JSON escaping, which is why this needs no hand-rolled escape pass.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTRUCTIONS="${SCRIPT_DIR}/../instructions.md"

# Fail loudly rather than emitting nothing. A hook that quietly produces no
# context is indistinguishable from a plugin that was never enabled, and that is
# the one failure mode a hook has that a plain instruction file does not.
if [ ! -r "${INSTRUCTIONS}" ]; then
  echo "pragma: cannot read ${INSTRUCTIONS}" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "pragma: jq is required and was not found on PATH" >&2
  exit 1
fi

jq -n --rawfile text "${INSTRUCTIONS}" \
  '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $text}}'
