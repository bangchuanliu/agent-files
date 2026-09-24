# Fan-out dispatch and `/fleet`

Background for fan-out dispatch, plus the dispatch rule itself. The hook `fanout-detect` injects
a short form of the rule on multi-item prompts; this file is the authoritative version.

## Dispatch rule

Treat each independent work item in a prompt (a numbered or bulleted list, several questions,
several files to change, or "do A, B and C" phrasing) as a separate item, and dispatch in order:

1. **1-2 items, or everything answerable in <=5 tool calls total**: handle it directly, batching
   all independent tool calls into a single message.
2. **>=3 independent items, OR any single item needing >5 tool calls**: launch one sub-agent per
   item with `mode: "background"`, with all launches emitted in ONE message.
3. After launching, never poll. State that you are waiting and end the turn; collect results with
   `read_agent` on notification.

Always apply rule 2 regardless of item count when the prompt contains "in parallel", "fan out",
"at the same time", "concurrently", or a leading `!!`. Sequence only where item N genuinely needs
item N-1's result, and say so. Report back per item, in the order asked.


## Why `mode: "background"` is required

`mode: "sync"` **blocks** the parent until the sub-agent returns. Launching five sync agents
runs them one after another - the wall-clock cost is identical to doing the work yourself, with
extra latency per agent. Only `mode: "background"` gets real parallelism, and only if **all
launches are emitted in a single message**. Launches split across messages serialize on the
parent's turn boundary.

After launching, **do not poll**. Completion notifications arrive automatically; `read_agent`
once per agent on notification. Polling burns turns and duplicates the agent's own work.

## Why this overrides the vendor default

Both Claude Code and Copilot CLI ship a "direct action first / prefer sync over background"
bias, tuned for single-threaded tasks where a sub-agent is pure overhead. That bias is wrong for
multi-item prompts. The trigger is **independence, not size**: separate files, separate tables,
separate questions = separate agents. Do not collapse a 5-item list into one serial pass because
each item looks small.

## `/fleet` is user-invoked, not agent-invoked

The agent **cannot run slash commands**. Writing "invoke /fleet" as an agent instruction is a
no-op. When a prompt contains a large or expensive multi-item batch:

1. Apply the AGENTS.md dispatch rule yourself, **and**
2. Tell the user, in one line, that `/fleet <task list>` would run it as vendor-orchestrated
   parallel subagents.

## Seed the todo graph before recommending `/fleet`

Fleet is a **scheduler, not a planner**. It dispatches the ready-set:

```sql
SELECT * FROM todos
WHERE status = 'pending'
  AND id NOT IN (SELECT todo_id FROM todo_deps WHERE depends_on IN
                 (SELECT id FROM todos WHERE status != 'done'));
```

With no `todo_deps` rows it fans out **everything** indiscriminately - including items that
conflict, e.g. two agents editing the same file. So before telling the user to run `/fleet`:

1. `INSERT` the todos, **and**
2. `INSERT` the real `todo_deps` edges.

Then recommend `/fleet`.

Sequence only where item N genuinely needs item N-1's result - and say so explicitly. Two
agents writing the same file is a dependency even when the tasks are logically independent.

## Reporting

Report back **per item, in the order asked**. Flag failed or ambiguous items individually rather
than silently dropping them.
