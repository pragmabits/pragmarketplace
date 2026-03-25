---
name: css
description: CSS expert — layouts, animations, responsive design, selectors, performance, SCSS/Sass/Less/PostCSS guidance
argument-hint: "[question or task] - e.g. \"center a div with flexbox\" or \"how to set up SCSS with Vite\""
---

# CSS Expert

Convenient entrypoint for the css agent. All CSS, SCSS, Sass, Less, and PostCSS guidance is handled by the agent.

## User Context

$ARGUMENTS

## Execution

### Resolve plugin root

Before invoking the agent, determine the absolute path to this plugin's root directory:

```
Plugin root: ${CLAUDE_PLUGIN_ROOT}
```

### Argument handling

If `$ARGUMENTS` is exactly `--resolve-root`:
- Output the plugin root path: `${CLAUDE_PLUGIN_ROOT}`
- Do not invoke the agent
- Stop here

### Invoke agent

Otherwise, invoke the css agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `css`
- **description**: "CSS expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's CSS question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Follow your Documentation Lookup Protocol and Project Context Detection steps. Verify answers against current documentation before responding.
```

This command does not answer questions directly. The css agent owns all CSS guidance — layouts, animations, responsive design, selectors, performance, and preprocessor patterns.
