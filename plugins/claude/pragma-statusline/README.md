# Pragma Statusline Plugin

Custom statusline for Claude Code with an Aura-themed display showing project info, git status, context usage, and session metrics.

## Overview

The Pragma Statusline plugin provides a `/pragma-status` command that installs a custom statusline script into Claude Code's `settings.json`. Once installed, the statusline replaces Claude Code's default status bar with a rich, color-coded display.

### What the Statusline Shows

```
project-name  main | ✓ ? ✗ ↑ ↓ | ✚ 42 ✘ 7 | 🧠 Claude 4 Opus | 🗗 35% | 🕐 2m 15s
```

| Section | Description |
|---------|-------------|
| **Project name** | Current workspace folder name (blue, bold) |
| **Git branch** | Current branch with status icons (purple) |
| **Git icons** | ✓ staged, ? modified/untracked, ✗ deleted, ↑ ahead, ↓ behind (dim) |
| **Lines changed** | Lines added (green) and removed (red) in session |
| **Model** | Active Claude model name (cyan) |
| **Context usage** | Context window percentage — blue (<50%), yellow (50-79%), red (≥80%) |
| **Duration** | Session duration formatted as Xh Ym Zs (yellow) |

## Available Commands

### `/pragma-status`

Installs the statusline into Claude Code settings.

**Usage:**
```
/pragma-status [user|local]
```

| Argument | Settings file | Description |
|----------|--------------|-------------|
| `user` (default) | `~/.claude/settings.json` | Global — applies to all projects |
| `local` | `.claude/settings.json` | Project-level — applies only to current project |

**Examples:**
```bash
# Install globally (default)
/pragma-status

# Install globally (explicit)
/pragma-status user

# Install for current project only
/pragma-status local
```

**What happens when you use `/pragma-status`:**

1. Resolves the absolute path to `scripts/statusline-command.sh`
2. Ensures the script is executable (`chmod +x`)
3. Merges the `statusLine` configuration into the target `settings.json` using `jq`
4. Reports the installed path and target file

**Settings format written:**
```json
{
  "statusLine": {
    "type": "command",
    "command": "/absolute/path/to/statusline-command.sh"
  }
}
```

## Requirements

- **jq** — used to merge configuration into `settings.json`
- **git** — for branch and status information in the statusline
- A terminal with ANSI color support

## Installation

This plugin is automatically loaded by Claude Code when present in the plugins directory.

**Expected location:**
- `~/.claude/plugins/pragma-statusline/` (global installation)
- `<project>/.claude/plugins/pragma-statusline/` (local installation)

## Troubleshooting

### Problem: Statusline not appearing after install

**Symptom:** Ran `/pragma-status` but the statusline doesn't show.

**Solution:** Restart Claude Code. Settings changes take effect on next launch.

---

### Problem: jq not found

**Symptom:** Error message about `jq` command not found.

**Solution:** Install jq — `sudo apt install jq` (Debian/Ubuntu), `brew install jq` (macOS), or equivalent for your system.

---

### Problem: Git icons not showing

**Symptom:** Branch name appears but icons (✓, ?, ✗, ↑, ↓) are missing.

**Solution:** Ensure your terminal supports Unicode characters and that git is available in `$PATH`.

## Versioning

- **Current version:** 1.0.0
- **Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH)

### Version History

#### v1.0.0 - March 2026
- **Initial release** with Aura-themed statusline
- `/pragma-status` command for user-level and project-level installation
- Git branch and status indicators (staged, modified, untracked, deleted, ahead, behind)
- Context window usage with color-coded thresholds
- Session duration and lines changed metrics
- ANSI color output with Nerd Font git branch icon

## Contributing

To add improvements:

1. Edit scripts in `scripts/`
2. Update `plugin.json` if necessary
3. Document in README.md
4. Test locally
5. Commit following repository conventions

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
**Company:** Pragmabits

---

**Version:** 1.0.0
**Updated:** March 2026
**Status:** Active
