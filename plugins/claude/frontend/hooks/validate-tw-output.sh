#!/bin/bash
set -euo pipefail

# Validate Tailwind CSS 4 patterns in Write/Edit tool calls.
# Warns on deprecated TW3 patterns, blocks direct contradictions.

input=$(cat)

# Extract file path and content based on tool type
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // ""')

# No file path or content — nothing to check
if [[ -z "$file_path" || -z "$content" ]]; then
  exit 0
fi

# Only check relevant file types
case "$file_path" in
  *.css|*.html|*.jsx|*.tsx|*.vue|*.svelte|*.astro)
    ;;
  *tailwind.config.js|*tailwind.config.ts|*tailwind.config.mjs)
    # Warn that CSS-first config is preferred in TW4
    cat >&2 <<'EOF'
{
  "systemMessage": "Warning: You are creating a tailwind.config file. In Tailwind CSS 4, CSS-first configuration via @theme is preferred over JavaScript config files. Consider using @theme in your CSS instead. If the user explicitly needs a JS config (e.g., for TW3 compatibility), proceed."
}
EOF
    exit 0
    ;;
  *)
    # Not a relevant file type
    exit 0
    ;;
esac

warnings=""

# Check 1: Deprecated @tailwind directives
if echo "$content" | grep -qE '@tailwind\s+(base|components|utilities)'; then
  # If the file also contains @import "tailwindcss", this is a contradiction — block
  if echo "$content" | grep -qE '@import\s+["\x27]tailwindcss["\x27]'; then
    cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "Blocked: File contains both @tailwind directives and @import \"tailwindcss\". This is contradictory. In TW4, use only @import \"tailwindcss\" — remove all @tailwind base/components/utilities directives."
}
EOF
    exit 2
  fi
  warnings="${warnings}\n- @tailwind directives are deprecated in TW4. Use @import \"tailwindcss\" instead of @tailwind base/components/utilities."
fi

# Check 2: Deprecated opacity utilities
if echo "$content" | grep -qoE '(bg|text|ring|border|placeholder)-opacity-[0-9]+'; then
  warnings="${warnings}\n- Deprecated opacity utilities detected (e.g., bg-opacity-50). In TW4, use the /XX opacity modifier instead (e.g., bg-black/50, text-white/75)."
fi

# Check 3: theme() function usage in CSS
if echo "$content" | grep -qE "theme\s*\("; then
  warnings="${warnings}\n- theme() function detected. In TW4, use CSS custom properties instead (e.g., var(--color-blue-500) instead of theme('colors.blue.500'))."
fi

# Check 4: @apply with deprecated utilities
if echo "$content" | grep -qE '@apply\s+.*\b(bg|text|ring|border|placeholder)-opacity-[0-9]+'; then
  warnings="${warnings}\n- @apply uses deprecated opacity utilities. Use opacity modifier syntax in @apply (e.g., @apply bg-black/50)."
fi

# If there are warnings, emit them as a system message
if [[ -n "$warnings" ]]; then
  message=$(printf "Tailwind CSS 4 lint warnings:%b\n\nConsider updating to TW4 patterns. If the user is intentionally using TW3, these warnings can be ignored." "$warnings")
  jq -n --arg msg "$message" '{"systemMessage": $msg}' >&2
  exit 0
fi

# All checks passed
exit 0
