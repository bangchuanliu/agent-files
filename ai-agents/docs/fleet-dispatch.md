# Fan-out dispatch

The authoritative rule for splitting a multi-item prompt across parallel sub-agents, with the
host-specific mechanics at the end.

## Dispatch rule

Treat each independent work item in a prompt (a numbered or bulleted list, several questions,
several files to change, or "do A, B and C" phrasing) as a separate item, and dispatch in order:

1. **1-2 items, or everything answerable in <=5 tool calls total**: handle it directly, batching
   all independent tool calls into a single message.
2. **>=3 independent items, OR any single item needing >5 tool calls**: launch one sub-agent per
   item, running concurrently, with all launches emitted in ONE message.
3. After launching, wait: state that you are waiting and end the turn, then collect each result
   once when its completion arrives.

Always apply rule 2 regardless of item count when the prompt contains "in parallel", "fan out",
"at the same time", "concurrently", or a leading `!!`. Sequence only where item N genuinely needs
item N-1's result, and say so. Two agents writing the same file is a dependency even when the
tasks are logically independent.

## Why concurrency needs one message

A blocking sub-agent call holds the parent until it returns, so five blocking launches run one
after another: the same wall-clock cost as doing the work yourself, plus per-agent latency. Real
parallelism needs non-blocking (or batched) launches, **all in a single message**; launches split
across messages serialize on the parent's turn boundary. Polling a running agent burns turns and
duplicates its work, so collect results only on completion.

## Why this overrides the vendor default

Host agents ship a "direct action first / prefer blocking sub-agents" bias, tuned for
single-threaded tasks where a sub-agent is pure overhead. That bias is wrong for multi-item
prompts. The trigger is **independence, not size**: separate files, separate tables, separate
questions = separate agents. A 5-item list of small items is still five agents.

## Host mechanics

| Host | Concurrent launch | Collect results |
|---|---|---|
| Copilot CLI | `task` with `mode: "background"`, all in one message | `read_agent` once per agent on its completion notification |
| Claude Code | several `Task` (Agent) tool calls in one message; they run concurrently | results return together when the batch finishes |
| Other hosts | whatever sub-agent tool exists, batched in one message | its completion mechanism |

With no sub-agent tool at all, work the items directly, still batching independent tool calls.

### Copilot CLI only: `/fleet`

`/fleet` is a user-typed slash command; the agent cannot run it. For a large or expensive batch,
apply the dispatch rule yourself **and** tell the user in one line that `/fleet <task list>` would
run it as vendor-orchestrated parallel sub-agents.

Fleet is a scheduler, not a planner: it dispatches every pending todo whose `todo_deps` are all
done, so with no dependency rows it fans out everything, including items that conflict. Before
recommending `/fleet`, insert the todos **and** their real `todo_deps` edges.

## Reporting

Report back **per item, in the order asked**. Flag failed or ambiguous items individually.
