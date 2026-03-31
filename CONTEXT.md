# Pragmarketplace Project Context

> This file is generated for Claude Code sessions. It captures the full architecture and conventions of this project so new sessions can quickly understand the codebase.

---

## 1. Project Purpose

**Pragmatic** is a curated collection of Claude Code plugins by Pragmabits. It's a marketplace of domain-specialized tools that extend Claude Code with:
- Specialized workflows (git commit strategy, frontend development)
- Knowledge bases (CSS, Vue.js, Tailwind CSS)
- Output formatting rules (guidelines/output styles)
- Custom CLI statuslines

All plugins live in `/plugins/claude/<plugin-name>` and are registered in `/.claude-plugin/marketplace.json`.

---

## 2. Directory Structure

```
pragmarketplace/
├── .claude/                      # Claude Code settings
│   ├── settings.json             # Permissions rules
│   └── settings.local.json       # Local overrides
├── .claude-plugin/
│   └── marketplace.json          # Central registry of all plugins
├── plugins/claude/               # All plugins
│   ├── git/                      # Git commit strategy
│   ├── css/                      # CSS expert agent
│   ├── frontend/                 # Frontend orchestrator (7 specialist agents)
│   ├── tailwindcss/              # Tailwind CSS 4 expert
│   ├── vuejs/                    # Vue.js / Nuxt 3 expert
│   ├── shadcn/                   # shadcn/ui expert
│   ├── fontawesome/              # Font Awesome expert
│   ├── guideline/                # Output style formatting rules
│   └── pragma-statusline/        # Custom statusline installer
└── README.md
```

### Individual Plugin Layout
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── README.md
├── commands/                     # Slash commands (entry points)
│   └── *.md
├── agents/                       # Sub-agents
│   └── *.md
├── skills/                       # Reusable domain units
│   └── skill-name/
│       ├── SKILL.md
│       └── evals/evals.json
├── hooks/                        # Validation/safety hooks
│   ├── hooks.json
│   └── *.sh
├── tools/                        # External executables
│   ├── *.pyz                     # Python zipapps
│   └── src/                      # Source for tools
├── scripts/                      # Utility/validation scripts
├── docs/                         # Internal documentation
└── styles/                       # Output styles (guideline plugin only)
```

---

## 3. Plugin Types

### Type A: Skill-Based (e.g., `guideline`)
- No slash command
- Provides output styles or skills only
- Example: `guideline` provides `pragmatic-autonomy` style

### Type B: Command + Single Agent (e.g., `git`, `css`, `tailwindcss`)
- One slash command entry point
- One agent handles all logic
- May include tools, skills, hooks

### Type C: Orchestrator + Specialists (e.g., `frontend`)
- Main command + specialist commands
- Orchestrator agent delegates to specialists
- Each specialist is its own agent

---

## 4. Plugin Manifest (`plugin.json`)

```json
{
  "name": "plugin-name",           // Must match directory name
  "version": "1.0.0",
  "description": "...",
  "author": { "name": "...", "email": "..." },
  "homepage": "https://...",
  "repository": "https://...",
  "keywords": ["tag1", "tag2"],

  // Only if plugin has commands:
  "commands": "./commands",

  // Only if plugin has agents:
  "agents": ["./agents/agent-name.md"],

  // Only if plugin has output styles:
  "outputStyles": "./styles/"
}
```

---

## 5. Command Structure (`commands/*.md`)

```markdown
---
name: command-name
description: Shown in /help
argument-hint: "[optional-arg]"
---

# Title

Description.

## User Context

$ARGUMENTS

## Execution

### Resolve plugin root

Plugin root: ${CLAUDE_PLUGIN_ROOT}

### Argument handling

If `$ARGUMENTS` is exactly `--resolve-root`:
- Output the plugin root path
- Stop here

### Invoke agent

Otherwise, use the Agent tool:
- subagent_type: plugin-name:agent-name
- prompt: ...includes $ARGUMENTS and ${CLAUDE_PLUGIN_ROOT}...
```

**Key points:**
- `${CLAUDE_PLUGIN_ROOT}` — resolved path to the plugin directory
- `$ARGUMENTS` — raw user input after the slash command
- Always handle `--resolve-root` special argument
- Commands delegate to agents; they don't do work themselves

---

## 6. Agent Structure (`agents/*.md`)

**Frontmatter:**
```yaml
---
name: agent-name
description: What this agent does
model: sonnet|opus|haiku
color: color-name
memory: user|disabled
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - WebFetch
  - WebSearch
  - Agent
  - TodoWrite
  - Skill
---
```

**Body structure:**
- Role definition
- Non-negotiable rules (3-4 critical constraints)
- Workflow steps
- When to use AskUserQuestion
- Delegation to other agents/skills
- Output format

**Invocation from command:**
```
subagent_type: "plugin-name:agent-name"
// or for single-agent plugins:
subagent_type: "plugin-name"
```

---

## 7. Skills Structure (`skills/<id>/SKILL.md`)

```markdown
---
name: skill-id
description: "When to use this. Trigger keywords. Examples."
---

Body: Why it exists, when to use it, how to invoke, patterns.
```

- Auto-discovered by Claude Code
- Invoked via `Skill` tool: `skill: "skill-id"`
- Include `evals/evals.json` with test cases

---

## 8. Hooks (`hooks/hooks.json`)

```json
{
  "description": "...",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/validate.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## 9. Output Styles (`styles/*.md`)

Only used in the `guideline` plugin.

```markdown
---
name: style-id
description: Human-readable name
keep-coding-instructions: true
---

Body: Rules and constraints applied to all agent interactions.
```

---

## 10. Evals (`skills/<id>/evals/evals.json`)

```json
{
  "skill_name": "skill-id",
  "evals": [
    {
      "id": 1,
      "prompt": "User input to test",
      "expected_output": "Description of desired behavior",
      "expectations": ["assertion 1", "assertion 2"]
    }
  ]
}
```

---

## 11. Marketplace Manifest (`.claude-plugin/marketplace.json`)

```json
{
  "name": "pragmatic",
  "owner": { "name": "pragmabits", "email": "..." },
  "metadata": { "description": "...", "version": "1.8.0" },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/claude/plugin-name",
      "description": "...",
      "version": "1.0.0",
      "author": { ... },
      "category": "tools|frontend|output",
      "commands": "./commands",
      "agents": ["./agents/agent.md"],
      "keywords": []
    }
  ]
}
```

---

## 12. Existing Plugins Summary

| Plugin | Type | Entry Points | Purpose |
|--------|------|-------------|---------|
| `git` | Command+Agent | `/commit`, `/tag-it`, `/commit-setup` | Semantic commits, staging, validation |
| `css` | Command+Agent | `/css` | CSS layouts, animations, responsive |
| `tailwindcss` | Command+Agent | `/tailwindcss` | Tailwind CSS 4 |
| `vuejs` | Command+Agent | `/vuejs`, `/nuxt` | Vue 3, Nuxt 3 |
| `shadcn` | Command+Agent | `/shadcn` | shadcn/ui components |
| `fontawesome` | Command+Agent | `/fontawesome` | Font Awesome icons |
| `frontend` | Orchestrator | `/frontend` + 7 specialist commands | Cross-domain frontend coordination |
| `guideline` | Style-based | (none) | Output formatting rules |
| `pragma-statusline` | Command+Script | `/pragma-status` | Custom statusline installer |

---

## 13. Key Architectural Principles

1. **Delegation over implementation** — commands → agents → specialists → skills
2. **Tool isolation** — declare exact Bash patterns needed; hooks validate at runtime
3. **Non-negotiable rules** — orchestrators list 3-4 critical rules that override everything
4. **AskUserQuestion for material decisions** — every user-facing choice goes through this tool
5. **Documentation-driven agents** — use context7 MCP + WebSearch, never rely on training data alone
6. **Skill granularity** — skills have one clear trigger condition and include evals
7. **Frontmatter metadata** — all config in YAML frontmatter (`---...---`)

---

## 14. Conventions

- **File naming**: kebab-case everywhere
- **Plugin root**: Always use `${CLAUDE_PLUGIN_ROOT}` (never hardcode paths)
- **Tool names**: Bash, Read, Write, Edit, Grep, Glob, Agent, Skill, AskUserQuestion
- **Error handling**: `&&` chains in Bash to stop on error
- **Versioning**: Update both `plugin.json` and `marketplace.json` on release
- **Agent communication**: AskUserQuestion for every user-facing decision
- **Permissions**: Document needed Bash patterns in `.claude/settings.json`

---

## 15. Reference Files

Key files to read when building a new plugin:

- `.claude-plugin/marketplace.json` — Plugin registry format
- `plugins/claude/git/.claude-plugin/plugin.json` — Simple plugin manifest
- `plugins/claude/git/commands/commit.md` — Command structure
- `plugins/claude/git/agents/commit-maker.md` — Agent role & workflow
- `plugins/claude/frontend/agents/frontend.md` — Orchestrator pattern
- `plugins/claude/frontend/skills/css-layout/SKILL.md` — Skill definition
- `plugins/claude/git/skills/commit/evals/evals.json` — Testing pattern
- `.claude/settings.json` — Permissions system
