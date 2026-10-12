---
name: yell
kind: leaf
description: "Use when: list every local coding-agent session (Herdr, terminal, or process-only) with its status and a follow-up / waiting / clean-up verdict, read-only - who needs me, which agents are done, what to pick up next, which sessions can be cleaned up, or the status of one named session. NOT for: starting a task stack (start), moving to a tab (hop), or creating or cleaning worktrees (wtree)."
---

# yell - who needs me?

## Objective

Show the user every coding-agent session on this machine, with a verdict on which ones need them now, without touching any session. It is the read-only companion to `start` and `hop`: a forgotten agent is exactly the one the user stopped looking at, so the inventory must be complete and nothing in it may be acted on without the user.

Success: the user sees every session in one table sorted by next step, can tell which need follow-up and why, and nothing on the machine changed.

## Context & Tools

`SKILL_DIR` is the directory containing this file. Run `"$SKILL_DIR/scripts/yell" [--json] [name-or-context...]`; `--help` lists the arguments. The wrapper checks for `jq`, then runs `scripts/yell.py`.

| User asks | Run |
|---|---|
| `yell`, "who needs me?", "what agents are done?" | `yell` - one table plus a "Why follow-up" reason per follow-up row |
| a named session or free-text context (`yell auth`, "the login work") | `yell <context>` - one detailed session; several candidates (exit 2) or no match (exit 1) |
| machine-readable output | `yell --json [context]` |

Verdicts, one per session and the table's sort key (rules in `next_step()` in `yell.py`):

- **follow-up** - needs the user: blocked on an approval or question, or finished with uncommitted or unpushed work, or finished with no terminal tab;
- **waiting** - still working, or not Herdr-managed with tty activity in the last 5 minutes; leave it alone;
- **clean-up** - finished or quiet with a clean tree; a suggestion to the user only.

Herdr is the lifecycle authority. An agent outside Herdr has status `unknown` and is tagged `[not Herdr-managed]` in the follow-up reasons, because only its process is known.

## Guardrails & Constraints

- MUST stay read-only while using this skill: report sessions and nothing else. MUST NOT start, stop, prompt, attach, detach, kill, close, focus, or open any session, pane, agent, or tab, or write git state; instead, name the action and let the user take it. `clean-up` is a suggestion, never an action.
- MUST show the overview table verbatim with all rows, because the table is the answer and the header count must match the rows the user sees. Keep its order and grouping; put commentary after it, only where it adds something the table cannot say.
- MUST describe an `unknown` agent as quiet or parked, never as finished, since nothing proves its turn ended.
- WHEN a context query matches several sessions, MUST show the candidates and ask the user which one they mean rather than picking one.
- WHEN a context query matches nothing, report that and offer the overview; WHEN Herdr or WezTerm sessions the user expects are absent, check whether `herdr` (`HERDR_BIN`) or `wezterm` (`WEZTERM_BIN`) is reachable, since the script silently falls back to the process table, and say which source was missing.
- MUST read a branch with `git -C <cwd> rev-parse --abbrev-ref HEAD`, never from a directory name.
- IF changing detection logic in `yell.py`, MUST keep every running agent in the output (the process-table sweep has the last word; a session may be described less richly but never dropped), and SHOULD buffer `herdr`, `ps`, and `wezterm` output before parsing rather than piping it into a short-circuiting consumer, which fails intermittently with SIGPIPE under `pipefail`.

## Verification

- The table shown to the user has the same row count as the script's header.
- IF `yell.py` changed, `python3 "$SKILL_DIR/tests/test_detection.py"` passes; it covers an agent tab dropped because a `herdr` process shared its tty, an agent with no WezTerm pane never being enumerated, and embedded or tty-less workers reported as sessions.
