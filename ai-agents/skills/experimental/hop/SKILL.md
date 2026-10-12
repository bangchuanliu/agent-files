---
name: hop
kind: leaf
description: "Use when: find or open the terminal tab for a branch, worktree, repo checkout, or directory - hop, go to, or switch to a branch, is there a tab or agent already there, jump me to it, open another tab there, just give me the path. NOT for: starting or resuming a task stack with worktree + Herdr + agent (start), live agent triage (yell), or creating/cleaning worktrees (wtree)."
---

# hop

## Objective

hop takes a branch, worktree, repo, or directory name and gets the user to a terminal tab sitting there: it reports a tab that already exists (and what agent runs in it), focuses it on request, or opens a new tab and resumes or starts the agent. An agent cannot change the user's shell directory, so hop works at the terminal-tab level and leaves the current session and all git state untouched; moving between independent worktree tabs then disturbs nothing.

Success: the destination path is reported (last stdout line of `hop.sh`), and either the existing tab and its agent are reported, the requested tab is focused, or a new tab is open there running the right command - with no duplicate agent and no change to git or the calling session.

## Context & Tools

- `scripts/hop.sh <branch-or-dir> [flags]` does the work. It has no `--help`; its flags:

  | Flag | Effect |
  |---|---|
  | (none) | resolve; report an existing tab, else open one |
  | `--focus` | jump to an existing tab, preferring one with an agent |
  | `--new-tab` | open another tab even if one exists |
  | `--no-focus` | a newly opened tab does not grab focus (unrelated to `--focus`, which is about existing tabs) |
  | `--tmux` / `--no-agent` / `--cmd <shell-cmd>` | run `tmux new-session -A`, a bare shell, or a custom command in the new tab instead of the agent; all three skip Herdr resume |
  | `--no-term` | resolve and print the path only |
  | `--repo-group <name>` | limit the branch match to one repo group under `$WTREE_ROOT` |

- Resolution, first match wins: an existing path; a worktree under `$WTREE_ROOT` whose checked-out branch equals the target or ends in `/<target>`; a worktree directory name; a repo under `DOTFILES_REPO_ROOTS` (default `$HOME/project`) one or two levels deep.
- With no tab open, hop resumes a live Herdr session found at the destination, else runs `$HOP_AGENT_CMD` (default `coya` if `copilot` is on PATH, else `cla`).
- `scripts/hop-term.py find|open|focus|herdr-session-for` is the WezTerm driver (`WEZTERM_BIN`, `HERDR_BIN` override paths). `find` returns JSON per tab with `cwd` (matched destination, possibly a Herdr pane inside the tab), `tab_cwd`, agents with Herdr status, `in_herdr`, and `in_tmux`. Use it directly only when `hop.sh` output is not enough.
- `scripts/hop-shell-init.sh`: optional shell function the user can source so `hop <target> --no-term` cds their own shell.

## Guardrails & Constraints

- MUST leave git state read-only: no commit, stash, checkout, branch, or worktree creation. Creating a worktree or task stack is `wtree` or `start`.
- MUST leave the calling session as it is: no `cd`, no pane close.
- MUST report, not switch, when a tab already exists at the destination; move the user only with `--focus` and duplicate only with `--new-tab`, each only when the user asked to jump or for another tab, because stealing focus or duplicating a live session disrupts work in progress. A request that does not say gets the default: report an existing tab, open one only when none exists.
- MUST keep one agent per worktree: when a detached Herdr session still owns the destination, resume it rather than starting a second agent beside it. Judge whether an agent is running from `hop.sh` / `hop-term.py find`, which ask Herdr, because `ps` on the tab's tty shows only `herdr` and misses the agent inside it.
- MUST NOT kill a pane, tmux session, Herdr session, or agent process; ending one is the user's call (`herdr session stop`, `wtree clean`).
- IF the target does not resolve, MUST stop and report, pointing at `wtree show` or `start <name>`; never create anything to make it resolve.
- IF the target could match several worktrees or repos, SHOULD state which path hop chose; IF that is not what the user meant, rerun with a full path or `--repo-group`.
- IF no tab can be opened (not WezTerm, or `wezterm cli` unavailable), MUST report that and give the user `cd <path>` instead of driving another terminal.

## Output

- The resolved path, the branch and uncommitted-change count `hop.sh` reports, and what happened: existing tab(s) with pane id and agent status, pane focused, or new pane opened and the command it runs.

## Verification

- `hop.sh` exited 0 and its last stdout line is an existing directory.
- WHEN a tab was opened or focused, `hop-term.py find <path>` lists it; WHEN a session was resumed, its agent appears once, not twice.
- State any step that could not be confirmed (for example the tab opened but agent readiness was not checked).
