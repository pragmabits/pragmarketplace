It is worth creating a **sub-agent** and using **looping** when that reduces operational complexity in a measurable way. If it does not, it becomes mere architectural ornamentation.

The central distinction is this:

- A **sub-agent** is for **separating responsibilities**.
- **Looping** is for **iterating until a stopping criterion is met**.

So the correct question is not “can it be used?”, but:

**“Is there a separable unit of work, and is there an objective criterion for repeating it?”**

## When it makes sense to create a sub-agent

Create a sub-agent when at least one of these cases applies:

1. **Clear specialization**
   A main agent decides the flow, and a secondary one executes a specific function:
   - analyze logs
   - write tests
   - summarize files
   - review diffs
   - classify tickets

2. **Context isolation**
   The main agent should not have to carry the entire context all the time.  
   Example: a sub-agent only receives the `billing/` module instead of the whole repository.

3. **Different tools**
   A sub-agent uses a specific set of commands, permissions, or heuristics.  
   Example: one agent to search files, another to run tests, another to validate output.

4. **Parallelization**
   You want to divide a problem into independent parts:
   - read 30 files
   - test 10 hypotheses
   - process N folders
   - generate multiple strategies and compare them

5. **Well-defined input/output contract**
   If you can state:
   - input: X
   - expected output: Y
   - failure: Z  
   then a sub-agent tends to work well.

## When a sub-agent is a bad idea

Do not use a sub-agent when:

- the task is linear and short
- the coordination cost is greater than the gain
- all agents need the same full context
- there is no way to evaluate the quality of the intermediate output
- the sub-agent only repeats vague instructions from the main agent

Rule of thumb:  
If you cannot describe the role of the sub-agent in **one objective sentence**, it probably should not exist yet.

Bad example:
> “a sub-agent to think better”

Good example:
> “a sub-agent to identify which tests failed and suggest the smallest fix compatible with the current diff”

---

## When looping makes sense

Looping is useful when the task is **iterative** and there is some verification mechanism.

Typical cases:

1. **Generate → evaluate → correct**
   Example:
   - generate code
   - run tests
   - analyze the error
   - fix it
   - repeat until it passes or reaches a limit

2. **Incremental search**
   Example:
   - search for relevant files
   - read the results
   - refine the query
   - search again

3. **Refinement with a metric**
   Example:
   - summarize
   - check topic coverage
   - supplement what is missing

4. **Batch execution**
   Example:
   - for each file, extract data
   - consolidate results
   - reprocess only the ones that failed

## When looping becomes a trap

Looping without a stopping criterion tends to degrade quickly.

Signs of a bad architecture:

- the loop “continues until it gets good”
- there is no metric or verifier
- each iteration adds more irrelevant context
- the agent starts oscillating between two solutions
- cost grows faster than quality

A good loop needs at least three things:

1. **stopping criterion**
2. **maximum iteration limit**
3. **way to evaluate progress**

Without that, you do not have a loop; you have a roulette wheel.

---

## Simple heuristic for deciding

Use this triage:

### Create a sub-agent if:
- the subtask is independent
- there is clear input/output
- the context can be reduced
- there is a gain from specialization or parallelization

### Use a loop if:
- there is verifiable feedback at each round
- there is a real possibility of incremental improvement
- you can define “done” without excessive subjectivity

### Use neither if:
- the task fits in a direct execution
- evaluation depends only on diffuse judgment
- coordination becomes more complex than the task

---

## Engineering rule: coordination cost

This is the most neglected point.

Every time you create a sub-agent, you introduce:

- prompt overhead
- context overhead
- state serialization
- risk of semantic loss between agents
- greater debugging difficulty

So the operational question is:

**Does the gain from decomposition outweigh the orchestration cost?**

If not, keep a single agent.

---

## Cases where it usually pays off

### 1. Automatic code fixing
Flow:
- the main agent chooses the target
- the sub-agent implements the fix
- the loop runs tests/linter
- a judge validates whether the fix was local and did not expand scope

This makes sense because there is objective verification.

### 2. Large codebase analysis
Flow:
- sub-agents analyze separate modules
- the main agent consolidates dependencies, risks, and hotspots

Here the gain comes from context isolation and parallelization.

### 3. Structured extraction across many files
Flow:
- the sub-agent reads a file
- extracts fields into JSON
- the loop reprocesses only schema errors

This makes sense because the output is validatable.

### 4. Multi-stage research
Flow:
- search agent
- reading agent
- critical agent to check inconsistencies
- loop until minimum source coverage is reached

This makes sense because each role is distinct.

---

## Cases where it usually does not pay off

### 1. “I want one agent that thinks, another that reviews, another that refines”
This is often architectural theater when:
- all of them do the same thing
- there is no objective evaluation
- the roles do not have real boundaries

### 2. Small shell tasks
Example:
- locate a file
- edit one line
- run one command

A good local loop or direct execution solves this better.

### 3. Environments with high risk of side effects
If the agent can:
- delete files
- deploy
- alter infrastructure
- modify a database

Sub-agent + looping without guardrails is an invitation to compounded error.

---

## Practical decision criteria

If you want an objective rule, use this mental matrix.

### Use a sub-agent when the subtask has:
- closed scope
- its own context
- explicit success criterion
- low need for continuous synchronization with the main agent

### Use a loop when there is:
- automatic feedback
- observable incremental improvement
- tolerance for trial and error
- controlled iteration budget

### Avoid it when there is:
- strong coupling between stages
- need for continuous global understanding
- absence of a verifier
- high cost per iteration

---

## Minimum healthy structure

If you are going to implement it, the minimum acceptable structure is:

1. **Explicit objective**
   E.g.: “fix tests in `payments` without changing the public interface”

2. **Sub-agent contract**
   E.g.: input = diff + logs; output = patch + brief justification

3. **Stopping criterion**
   E.g.: all target tests passed, or 5 iterations, or confidence below threshold

4. **Guardrails**
   E.g.:
   - do not execute `rm -rf`
   - do not alter files outside `src/payments`
   - do not commit automatically

5. **Observability**
   Log:
   - hypothesis
   - executed command
   - result
   - reason for the next iteration

Without observability, you are not debugging the system; you are merely watching it fail.

---

## Short rule that usually works

Ask:

1. **Can I decompose this task without losing understanding?**
2. **Can I measure whether each iteration improved it?**
3. **Can I limit cost and damage if it goes wrong?**

If the answer is “yes” to all three, sub-agent + looping may be worth it.

If the answer is “no” to the second, it is almost certainly not worth it.

---

## My operational recommendation

In a terminal agent tool, start with this gradient:

1. **single execution**
2. **single execution with tools**
3. **simple loop with a limit**
4. **one specialized sub-agent**
5. **multiple sub-agents only after proving gain**

In other words:  
**do not start with the most “intelligent” architecture; start with the smallest architecture that already delivers reliable results.**

This avoids a common mistake: using multi-agent design to compensate for a bad prompt, lack of context, or absence of a verifier.

If you want, I can give you a **decision framework as a technical checklist** or a **concrete CLI architecture example with planner + worker + judge + bounded loop**.