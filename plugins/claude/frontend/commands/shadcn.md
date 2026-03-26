---
name: shadcn
description: shadcn/ui expert — component setup, CLI guidance, theming, and framework integration
argument-hint: [question or task] - e.g. "set up shadcn in my Next.js project" or "how to change the primary color"
---

# shadcn/ui Expert

Convenient entrypoint for the shadcn agent. All component setup, CLI guidance, theming, configuration, and framework integration is handled by the agent.

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

Otherwise, invoke the shadcn agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `shadcn`
- **description**: "shadcn/ui expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's shadcn/ui question using the official documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Look up the relevant documentation files at <plugin-root>/docs/shadcn/web/ before answering. Use Read, Glob, and Grep to find the information you need. Always verify your answers against the docs.

For project-specific guidance, check for components.json and package.json in the user's project to understand their framework, installed components, and configuration.
```

### Post-agent: Commit strategy

After the agent returns, apply the commit strategy protocol from `<plugin-root>/references/commit-strategy.md`:

1. If `$ARGUMENTS` contains `ORCHESTRATED=true`, skip — the orchestrator handles commits
2. If the agent did not modify any files (pure Q&A), skip
3. Otherwise, detect available commit strategies from the session context (skill/agent names containing "commit")
4. Present AskUserQuestion with detected options + "Do not commit"
5. Execute the user's chosen strategy

This command does not answer questions directly. The shadcn agent owns all component guidance, CLI reference, theming advice, and framework-specific patterns.
