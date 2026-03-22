#!/bin/bash
set -euo pipefail

# Validate git commands to prevent interactive or problematic patterns.
# Blocks: git add -p (interactive), git -C (path issues with staging tool),
# git config user.name/email (intrusive identity changes).

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# No command — nothing to check
if [[ -z "$command" ]]; then
  exit 0
fi

# Only check git commands
if ! echo "$command" | grep -qE '(^|\s|&&|\|\||;)git\s'; then
  exit 0
fi

# Block git add -p / --patch (interactive, fails in headless environments)
if echo "$command" | grep -qE 'git\s+add\s+.*(-p|--patch)'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "git add -p is blocked because it requires interactive input. Use the staging tool (git-staging.pyz stage) for hunk-level staging instead."
}
EOF
  exit 2
fi

# Block git -C flag (causes path resolution issues with staging tool)
if echo "$command" | grep -qE 'git\s+-C\s'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "git -C flag is blocked because it causes path resolution issues with the staging tool and validator. Run git commands from the repository working directory instead."
}
EOF
  exit 2
fi

# Block git config user.name / user.email modifications
if echo "$command" | grep -qE 'git\s+config\s+(--global\s+)?user\.(name|email)'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "Modifying git user.name or user.email is blocked. The user's git identity is already configured — changing it would be intrusive."
}
EOF
  exit 2
fi

# All checks passed
exit 0
