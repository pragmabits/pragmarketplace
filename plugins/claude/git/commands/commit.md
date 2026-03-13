---
name: commit
description: Strategic commits using intelligent repository analysis
argument-hint: [context or instruction] - e.g. "complete feature" or "split by context"
---

# Strategic Git Commit

Convenient entrypoint for the git-orchestrator agent. All commit logic — analysis, staging, validation, partitioning, and execution — is handled by the agent.

## User Context

$ARGUMENTS

## Execution

Invoke the git-orchestrator agent to handle the commit workflow:

Use the Task tool with:
- **subagent_type**: `git-orchestrator`
- **description**: "Strategic commit analysis"
- **prompt**: Include the user context below, then instruct the agent to execute its full workflow.

Prompt template:
```
Execute your full commit workflow for this repository.

User context: $ARGUMENTS

Analyze the working tree, determine the commit strategy, validate messages, and execute commits following your complete workflow.
```

This command does not perform commits directly. The git-orchestrator agent owns all commit decisions, validation, and execution.
