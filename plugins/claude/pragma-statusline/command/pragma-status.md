---
name: pragma-status
description: Install the pragma statusline into Claude Code settings
argument-hint: "[user|local] - target settings level (default: user)"
---

# Install Pragma Statusline

Installs the statusline script into Claude Code's `settings.json`.

## Arguments

`$ARGUMENTS` — either `user` (default) or `local`.

## Execution

Run the following bash commands to install the statusline:

```bash
# Parse argument — default to "user"
LEVEL="${1:-user}"

# Validate
if [[ "$LEVEL" != "user" && "$LEVEL" != "local" ]]; then
  echo "Error: argument must be 'user' or 'local', got '$LEVEL'"
  exit 1
fi

# Resolve absolute path to the statusline script
SCRIPT_PATH="${CLAUDE_PLUGIN_ROOT}/scripts/statusline-command.sh"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "Error: statusline script not found at $SCRIPT_PATH"
  exit 1
fi

# Ensure executable
chmod +x "$SCRIPT_PATH"

# Determine target settings file
if [[ "$LEVEL" == "user" ]]; then
  SETTINGS_FILE="$HOME/.claude/settings.json"
else
  SETTINGS_FILE=".claude/settings.json"
fi

# Ensure directory exists
mkdir -p "$(dirname "$SETTINGS_FILE")"

# Merge statusLine config into settings using jq
if [[ -f "$SETTINGS_FILE" ]]; then
  EXISTING=$(cat "$SETTINGS_FILE")
else
  EXISTING="{}"
fi

echo "$EXISTING" | jq --arg cmd "$SCRIPT_PATH" '.statusLine = {"type": "command", "command": $cmd}' > "$SETTINGS_FILE"

echo "Statusline installed at $LEVEL level: $SETTINGS_FILE"
echo "Script path: $SCRIPT_PATH"
```

Use Bash to execute the script above. Replace `$1` with the parsed value from `$ARGUMENTS` (default to `user` if `$ARGUMENTS` is empty). Use `${CLAUDE_PLUGIN_ROOT}` directly — it is available as a shell variable at runtime.

After execution, confirm to the user:
- Which settings file was updated
- The absolute path written to the `statusLine.command` field
