---
name: htmx-go
description: HTMX + Go expert — attributes, templ components, server handlers, SSE/WebSocket, and Go integration
argument-hint: "[question or task] - e.g. \"how do I return an HTMX fragment in chi\" or \"set up SSE with templ\""
---

# HTMX + Go Expert

Convenient entrypoint for the htmx-go agent. All HTMX attribute guidance, Go handler patterns, a-h/templ components, real-time SSE/WebSocket patterns, and HTMX+Go integration questions are handled by the agent.

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

Otherwise, invoke the htmx-go agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `frontend:htmx-go`
- **description**: "HTMX + Go expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's HTMX + Go question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Follow your Documentation Lookup Protocol and Project Context Detection steps. Verify answers against current documentation before responding.
```

### Post-agent: Commit strategy

After the agent returns, apply the commit strategy protocol from `<plugin-root>/references/commit-strategy.md`:

1. If `$ARGUMENTS` contains `ORCHESTRATED=true`, skip — the orchestrator handles commits
2. If the agent did not modify any files (pure Q&A), skip
3. Otherwise, detect available commit strategies from the session context (skill/agent names containing "commit")
4. Present AskUserQuestion with detected options + "Do not commit"
5. Execute the user's chosen strategy

This command does not answer questions directly. The htmx-go agent owns all HTMX and Go guidance — attributes, extensions, handlers, templ components, forms, SSE, WebSocket, and routing patterns.
