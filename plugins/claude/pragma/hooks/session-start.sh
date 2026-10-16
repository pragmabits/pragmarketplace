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

# The review gate's contract rides along only while the gate is on, so turning
# the gate off (see README) leaves the directives above exactly as they were.
GATE_CONTRACT="${SCRIPT_DIR}/../gate/contract.md"
GATE_CONFIG="${PRAGMA_GATE_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/pragma/gate.json}"
gate_on=1
gate_env="${PRAGMA_GATE:-}"
case "${gate_env,,}" in off|0|false|disabled) gate_on=0 ;; esac
if [ -r "${GATE_CONFIG}" ] && [ "$(jq -r '.enabled' "${GATE_CONFIG}" 2>/dev/null)" = "false" ]; then
  gate_on=0
fi
if [ "${gate_on}" = 1 ] && [ -r "${GATE_CONTRACT}" ]; then
  jq -n --rawfile text "${INSTRUCTIONS}" --rawfile gate "${GATE_CONTRACT}" \
    '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: ($text + $gate)}}'
else
  jq -n --rawfile text "${INSTRUCTIONS}" \
    '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $text}}'
fi
