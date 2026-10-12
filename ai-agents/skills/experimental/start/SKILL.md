---
name: start
kind: orchestrator
description: "Use when: create or resume one task stack - a slug-named Herdr session, wtree worktree, terminal tab, and agent - start a task, start a new task, do task, spin up a workspace for X, resume the X session, is the X task already running. NOT for: creating a worktree alone (wtree), moving to an existing tab or path (hop), live agent triage (yell), or committing finished work."
---

# start

## Objective

start turns a task into one running stack - a Herdr session, a git worktree, a terminal tab, and an agent, all named from one slug - or reports that the stack already exists and resumes it if its tab was closed. One task per stack keeps work isolated, and checking state before creating anything makes a repeated `start` safe.

Success: `scripts/start.sh` ends with one stdout line, `CREATED`, `RESUMED`, or `ALREADY_RUNNING` (or a `--status` line), reported to the user, with no duplicate session, tab, worktree, or agent.

## Context & Tools

- `scripts/start.sh <slug> [repo-group] [flags]` does the work; `--help` lists flags. It also takes `--repo-group <name>`, `--base <ref>` (worktree base; default is wtree's `origin/HEAD`), and `--no-focus` (new tab does not grab focus).
- State decides the action:

  | Session | `herdr --session <slug>` client attached | Result |
  |---|---|---|
  | absent | - | `CREATED`: worktree via `wtree-new.sh`, new WezTerm tab at `$HOME` running `herdr --session <slug>`, pane `cd`'d into the worktree, agent started |
  | running or stopped | none | `RESUMED`: new tab re-attaches; no worktree, no agent |
  | running | yes | `ALREADY_RUNNING`: tty and pane reported; nothing changes |

- One slug names everything: session and Herdr agent `<slug>`, branch `<owner>/<slug>`, worktree `$WTREE_ROOT/<repo-group>/<owner>-<slug>` (owner is `WTREE_BRANCH_PREFIX` or `$USER`). Lookup also accepts the older `<owner>-<slug>` session name.
- Agent: kind `DO_AGENT_KIND`, else `copilot` if on PATH, else `claude`; launched with `--autopilot --allow-all` (Copilot) or `--dangerously-skip-permissions` (Claude) unless `START_AGENT_ARGS` overrides. If `herdr agent start` does not confirm readiness, the script runs `START_AGENT_CMD`, `HOP_AGENT_CMD`, or `coya`/`cla` in the pane.
- Depends on `herdr` and `jq` on PATH, the sibling `wtree` skill's `wtree-new.sh`, and the `hop` skill's `hop-term.py` (WezTerm). A closed tab leaves the Herdr session and its agent alive; `start <slug>` or `hop <slug>` reattaches.

## Guardrails & Constraints

- MUST derive the slug yourself: a 2-4 word kebab-case topic from the requirement ("fix the login retry double count" -> `login-retry-dedup`), because it becomes the branch, worktree, and session name. Proceed on your choice without asking to confirm it.
- MUST choose the repo before creating, because the branch, session, and agent are all built on it and a wrong repo is costly to unwind:
  - inside a git repo, pass no repo group (wtree resolves it and hops from a worktree back to its main clone);
  - outside one, infer the repo from the task and pass it;
  - IF the repo is ambiguous or low-confidence, MUST ask the user.
- IF wtree reports `no git repo named '<name>' under configured repo roots`, MUST check `DOTFILES_REPO_ROOTS` (default `$HOME/project`) covers the repo and rerun with it set, before concluding the repo does not exist.
- MUST open the session from a real terminal tab via `start.sh`; MUST NOT substitute `herdr tab create` or launch from inside a Herdr pane, because Herdr refuses to nest.
- MUST leave a resumed or already-running stack alone: no new worktree, no second agent, no second tab, no focus steal. Taking the user to an existing tab is `hop --focus`.
- MUST leave the calling session as it is: no `cd`, commit, stash, or pane close. The only writes are a new tab, session, worktree, and agent.
- MUST NOT stop, kill, or remove a session, pane, agent, or worktree; teardown is the user's call (`herdr session stop <slug>`, `wtree clean`).
- IF `start.sh` exits non-zero (missing `herdr`/`jq`, wtree failure, no WezTerm tab, session not running in time), MUST stop and report its error and whatever it already created (for example the worktree or tab pane), rather than retrying with another terminal or cleaning up. A wtree failure aborts before any tab opens.
- IF the user only wants to know whether a task is running, MUST use `--status`; IF they want the plan without side effects, use `--dry-run`.
- SHOULD honour a request to skip parts with `--no-worktree` (session starts in `$HOME`) or `--no-agent`.

## Output

- The final stdout line of `start.sh` (state, slug, session, pane, worktree), plus any fallback or warning it logged on stderr.

## Verification

- The final line is `CREATED`, `RESUMED`, `ALREADY_RUNNING`, or a `--status` line, and exit code is 0.
- WHEN `CREATED` or `RESUMED`, `start.sh <slug> --status` shows the session `running` with an attached tty.
- WHEN `CREATED` with an agent, the agent appears once in `herdr --session <slug> agent list`; state it if readiness could not be confirmed.
