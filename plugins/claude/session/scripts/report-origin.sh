#!/usr/bin/env bash
# report-origin.sh — authorship header lines for a report being written now.
#
# Usage: report-origin.sh
#
# Prints the header lines to copy, then "#" lines saying where each value came
# from. Every value rests on a documented source:
#
#   **Harness:** claude-code   CLAUDECODE=1, which Claude Code documents as set
#                              in the subprocesses it spawns; "unknown" otherwise
#   **Report generator:** session/claude-code <version>
#                              read from this plugin's own manifest
#
# There is no Model line. Claude Code documents no way for a skill or the shell
# it spawns to learn the model serving the current turn: ANTHROPIC_MODEL and
# the model setting are configured defaults, the transcript's entry format is
# documented as internal, and the documented sources (status line input,
# SessionStart and model-switch hooks) would need a hook added just for this.
# A field that could only ever say "unknown" is left out instead.
#
# Harness version is left out too: no documented source gives the version of
# the running process to a skill, and a `claude` found on PATH may be another.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

harness="unknown"
[[ "${CLAUDECODE:-}" == "1" ]] && harness="claude-code"

version="$(sed -n 's/^[[:space:]]*"version":[[:space:]]*"\([^"]*\)".*/\1/p' "${PLUGIN_ROOT}/.claude-plugin/plugin.json" 2>/dev/null | head -n1)"

printf '**Harness:** %s\n' "$harness"
printf '**Report generator:** session/claude-code%s\n' "${version:+ ${version}}"
printf '# No Model line: no documented source gives a skill the model of the current turn\n'
printf '# No Harness version line: no documented source for the running process\n'
