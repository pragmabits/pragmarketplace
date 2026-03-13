---
name: commit
description: Strategic commits using intelligent repository analysis
argument-hint: [context or instruction] - e.g. "complete feature" or "split by context"
---

# Strategic Git Commit

Convenient entrypoint for the commit-maker agent. All commit logic — analysis, staging, validation, partitioning, and execution — is handled by the agent.

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

Otherwise, invoke the commit-maker agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `commit-maker`
- **description**: "Strategic commit analysis"
- **prompt**: Include the plugin root and user context, then instruct the agent to execute its full workflow.

Prompt template:
```
Execute your full commit workflow for this repository.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Analyze the working tree, determine the commit strategy, validate messages, and execute commits following your complete workflow.
```

This command does not perform commits directly. The commit-maker agent owns all commit decisions, validation, and execution.
