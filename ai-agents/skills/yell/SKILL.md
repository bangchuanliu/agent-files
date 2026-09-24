---
name: yell
kind: orchestrator
description: "Report every local coding-agent session in one table — Herdr-managed and plain terminal tabs alike — with branch, directory, what it was doing, agent age, status, and a next-step verdict of follow-up / waiting / clean-up. Use when: yell, who needs me, what agents are done, what should I pick up next, which sessions can I clean up, status for a named session. NOT for: starting task stacks (start), moving to a tab yourself (hop), or creating and cleaning worktrees (wtree)."
---

# yell — who needs me?

`yell` is the read-only companion to `start` and `hop`: it inventories coding-agent
sessions on this Mac and answers, “which agents are waiting for me?”

## Usage

```bash
"$SKILL_DIR/scripts/yell" [--json] [name-or-context...]
```

| User says | Run |
|---|---|
| `yell` / "who needs me?" / "what agents are done?" | `"$SKILL_DIR/scripts/yell"` |
| `yell auth` / `yell "the login work"` | `"$SKILL_DIR/scripts/yell" auth` |
| "machine-readable yell" | `"$SKILL_DIR/scripts/yell" --json` |
| "JSON for the code-review session" | `"$SKILL_DIR/scripts/yell" --json code-review` |

Requires `python3` and `jq`.

## What no-argument mode reports

**One table, every agent session on the machine** — Herdr-managed and not. Nothing is
hidden in a second table, because a forgotten agent is exactly the one you stopped
looking at.

```
┌───────────────────────┬─────────────────────────┬────────────────────────┬────────────────────┬────────────┬───────────┐
│ branch                │ Directory               │ What it was doing      │ Agent age          │ Status     │ Next step │
├───────────────────────┼─────────────────────────┼────────────────────────┼────────────────────┼────────────┼───────────┤
│ banliu/code-review    │ ~/.worktree/…/code-rev… │ Update Review Others   │ Sep 23 22:36 (1h)  │ idle 8m    │ follow-up │
│ master                │ ~/project/app/ots-revie… │ Generate New Sheet     │ Sep 14 (9d)        │ unknown 2h │ follow-up │
│ master                │ ~/temp/offsite-trackin… │ Check Login Metrics   │ Sep 22 (36h)       │ unknown 0s │ waiting   │
└───────────────────────┴─────────────────────────┴────────────────────────┴────────────────────┴────────────┴───────────┘
```

- **Agent age** — when the agent process actually started, from `ps etime`. For a
  Herdr agent the process lives inside the server's pty, so it is found by walking the
  process tree down from the attached client; if the session is detached, the session
  directory's birth time is the fallback.
- **Status** — lifecycle plus idle time. `working` has no idle time by definition.
- **Next step** — the whole point of the table; see below.

Under the table, every `follow-up` row gets a one-line reason, tagged
`[not Herdr-managed]` where the status is only inferred.

## Presenting the output

**Show the table verbatim, all rows.** Do not re-sort it, do not split it into your own
grouped tables, and do not drop rows you judge uninteresting — the count in the header
must match the rows the user sees. The table is already sorted by next step and is the
answer; an agent that summarises it into prose has thrown away the thing that was asked
for.

Commentary belongs after the table, and only where it adds something the table cannot
say on its own.

## Next step

Exactly one of three verdicts per session, and the sort key for the table:

| Verdict | Meaning |
|---|---|
| **follow-up** | needs you: blocked on an approval, or finished with work left behind |
| **waiting** | the agent is still going; leave it alone |
| **clean-up** | finished with nothing to save — tear it down |

Rules, first match wins:

1. `blocked` → **follow-up** — an approval/question dialog is literally waiting.
2. `working` → **waiting**.
3. `unknown` and touched in the last 5 min → **waiting**. Not Herdr-managed, so a live
   turn cannot be ruled out; recent tty activity is the only evidence available.
4. uncommitted or unpushed work → **follow-up**. Detected with `git status --porcelain`
   and `git rev-list --count HEAD --not --remotes`.
5. `unknown` and quiet with a clean tree → **clean-up**.
6. ready with no terminal tab → **follow-up** — finished and invisible.
7. otherwise → **clean-up**.

`unknown` is never *claimed* to be finished. Herdr is the lifecycle authority; for an
agent outside it, all that is really known is that a `copilot`/`claude` process exists.

## Context mode

With a name or free-text context, `yell` matches over:

- Herdr session name
- pane cwd and cwd basename
- git branch from `git -C <cwd> rev-parse --abbrev-ref HEAD`
- pane title / terminal title
- Herdr pane id

Resolution is conservative. An exact match reports one detailed session. If a substring or
fuzzy query matches several sessions, `yell` lists candidates instead of guessing.

## Detection model

`yell` combines three sources, and reports **every** agent it finds in one table:

- Herdr sessions: `herdr session list --json` (override the binary with `HERDR_BIN`), then per-session
  `pane list`, `agent list`, and `tab list`. Per-session calls always use
  `herdr --session <name> ...`.
- Attached Herdr clients: `ps -eo pid,tty,command` rows whose command is exactly
  `herdr`, `herdr --session <name>`, or `herdr session attach <name>`, mapped to WezTerm
  panes by `.tty_name` from `wezterm cli list --format json`.
- Plain WezTerm agents: WezTerm panes whose tty hosts a `copilot` or `claude` process
  that Herdr does not own. Their status is `unknown` — never `done` — because Herdr is
  the lifecycle authority, but they appear in the same table as everything else.
- Agents with no pane at all: a final sweep of the process table picks up any
  `copilot`/`claude` process that neither of the above claimed — an agent started
  outside WezTerm, inside a multiplexer, or in a pane WezTerm reports without a tty.
  Their working directory comes from `lsof -a -p <pid> -d cwd`. Pane enumeration is the
  fragile part of detection, so the process table gets the last word: a running agent
  can be described less richly, but it can never be missing.
- Ownership, i.e. which side reports an agent, is decided by process ancestry: a Herdr
  agent always runs inside a pty owned by a `herdr server`, so descending from a server
  process is the test. "Some process named `herdr` shares this tty" is *not* the test —
  an agent tab that merely shells out to `herdr` is still a plain tab.
- A logical session is the topmost agent process; the CLI launcher re-execs itself, so
  a single session appears as an agent parented by another agent.
- Agent age: `ps -eo pid,ppid,tty,etime,comm` (macOS has `etime`, not `etimes`). A Herdr
  agent is found by walking the process tree down from the attached client, since it runs
  on the server's own pty rather than the tab's tty. `comm` and `args` are read in
  separate `ps` calls, because asking for both at once makes macOS truncate `comm` to 16
  characters and destroys the executable basename.

Producer output is buffered before parsing. The scripts do not pipe `herdr`, `ps`, or
`wezterm` into short-circuiting consumers, avoiding intermittent SIGPIPE / exit-141
failures under `set -o pipefail`.

## Safety rules

- **Strictly read-only. `yell` reports and nothing else.** It never starts, stops,
  prompts, attaches, detaches, kills, closes, or opens a session, pane, agent, or
  terminal tab, and never writes git state.
- Git inspection is read-only (`rev-parse`, `status`, `rev-list`) and branches are never
  parsed from worktree directory names.
- An `unknown` agent is never reported as finished, and is never torn down on its own
  say-so — `clean-up` is a suggestion to you, not an action `yell` takes.
- Ambiguous context is reported as candidates; the script does not pick a session on the
  user's behalf.

## Tests

```bash
python3 "$SKILL_DIR/tests/test_detection.py"
```

Regression coverage for the two ways a live agent used to vanish: a plain agent tab
dropped because a `herdr` command shared its tty, and an agent with no WezTerm pane
never being enumerated.

## Related

- `start` starts or resumes a task stack: Herdr session + worktree + agent.
- `hop` focuses or opens terminal tabs for known directories.
- `wtree` creates, lists, and safely cleans worktrees with agent-session awareness.
