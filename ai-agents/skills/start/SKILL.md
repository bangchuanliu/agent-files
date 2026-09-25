---
name: start
kind: orchestrator
description: "Start: create or resume one task stack: slug, Herdr session, wtree-created worktree, terminal tab, and agent command. Use when: start task, start a new task, do task, new session for this, spin up a workspace for X, resume the X session. NOT for: creating a worktree alone (wtree), moving to a known tab or path (hop), live agent triage (yell), long-horizon project status (where-are-we), or committing finished work."
---

# do - one tab, one session, one worktree, one agent per task

Every task gets its own Herdr session, git worktree, terminal tab, and configured agent
command. `start` makes that whole stack exist - or tells you it already does. The agent kind
is `DO_AGENT_KIND`, else `copilot` if on PATH, else `claude`; its launch args and fallback
alias (`coya` / `cla`) follow the kind, overridable with `START_AGENT_ARGS` and
`START_AGENT_CMD` (or `HOP_AGENT_CMD`).

## Usage

```bash
"$SKILL_DIR/scripts/start.sh" <slug> [repo-group] [flags]
```

**You derive the slug**, not the script. Turn the requirement into a short kebab-case
topic - "fix the login retry double count" -> `login-retry-dedup` - 2–4 words, dropping
filler verbs. The script re-normalizes whatever you pass, so a whole sentence still
works, but a sentence makes an ugly branch and a truncated session name. Pick the name
yourself and go; do not stop to confirm it.

| User says | Run |
|---|---|
| `start <task description>` / "start a new task" | `start.sh <slug>` |
| "...in the `<repo-group>` repo" | `start.sh <slug> <repo-group>` |
| task names a repo you are not currently in | `start.sh <slug> <repo-group>` - see "Which repo" below |
| "just tell me if it's running" | `start.sh <slug> --status` |
| "no worktree, just a session" | `start.sh <slug> --no-worktree` |
| "open it but don't start the agent" | `start.sh <slug> --no-agent` |
| "don't yank my focus" | `start.sh <slug> --no-focus` |

Flags: `--repo-group <name>`, `--base <ref>`, `--no-worktree`, `--no-agent`, `--no-focus`,
`--status`, `--dry-run`.

## Which repo - you resolve this, not the script

`wtree` is deliberately mechanical: given a repo group name it looks under configured roots, and given
nothing it uses the current git repo. It does not guess. **Working out which repo a task
belongs to is your job**, because it needs the conversation, and a shell script does not
have that.

Resolve in this order:

1. **Already inside a git repo** - pass no repo group. `wtree` resolves it, and hops from a
   worktree back to its main clone, so you cannot nest a worktree inside a worktree.
2. **Not in a git repo** (e.g. the tab starts at `~`) - work the repo out from the task
   itself and pass it explicitly. "split banliu-dotfiles into two repos" names its repo;
   "fix the login retry double count" implies `example-service` from the domain.
3. **Genuinely ambiguous or low confidence** - ask the user which repo, and do not guess.
   A worktree cut from the wrong repo is worse than one question, because the branch,
   session and agent all get built on top of the mistake before anyone notices.

### Repos outside `$HOME/project`

`wtree` searches `DOTFILES_REPO_ROOTS`, a colon- or space-separated list that defaults to
`$HOME/project`. A repo outside that default root must be covered by the variable:

```bash
DOTFILES_REPO_ROOTS="$HOME/project:$HOME/other" "$SKILL_DIR/scripts/start.sh" <slug> my-repo
```

Without the right root the failure is `wtree-new: no git repo named '<name>' under
configured repo roots` - that message means wrong *root*, not missing repo, so check the
path before concluding the repo does not exist.

## One slug, one identity

The slug is the only name in play. Everything else is that same string with the
separator each layer allows:

| Thing | Name | Example |
|---|---|---|
| Herdr session | `<slug>` | `login-retry-dedup` |
| branch | `<owner>/<slug>` | `banliu/login-retry-dedup` |
| worktree dir | `<owner>-<slug>` | `~/.worktree/<repo-group>/banliu-login-retry-dedup` |
| Herdr agent | `<slug>` | `login-retry-dedup` |

The owner prefix comes from `wtree` (`$USER`, or `WTREE_BRANCH_PREFIX`); the flattening
of `/` to `-` is `wtree`'s path slug. So given any one of the four you can read off the
other three - `herdr session list` and `wtree show` line up row for row.

Session **lookup** accepts the owner-prefixed form too (`banliu-login-retry-dedup`), so
sessions named before this convention still resume instead of being recreated. Anything
new is created under the bare slug.

## Closing a tab is safe

A Herdr session outlives its terminal tab. Closing the tab detaches the client; the
session, its panes, its cwd and its agent all keep running. Both `start <slug>` and
`hop <slug>` will reattach you to that same agent - neither starts a second one.

Use `herdr session stop <slug>` when you actually want the agent gone.

## The three states

Two independent facts decide everything: does the session exist
(`herdr session list --json`), and is a `herdr --session <slug>` client attached to it
(a process in the table, whose tty identifies the terminal tab). A Herdr session keeps
running with no client attached, so "is there a tab" is a process question, not a
session question. The process match is anchored at end-of-command and requires a real
tty, so a transient `herdr --session <slug> pane list` API call is not mistaken for an
attached client.

| Session | Attached client | Action | stdout |
|---|---|---|---|
| absent | - | **create** the full stack | `CREATED` |
| running or stopped | none | **resume** - new tab, re-attach | `RESUMED` |
| running | yes | **nothing** - report it | `ALREADY_RUNNING` |

Report the final stdout line to the user; everything else is commentary on stderr.

### create

1. `wtree-new.sh <slug> [repo-group]` - worktree cut from `origin/HEAD`, never from the current
   checkout. Its path is the last line of output.
2. A new **terminal tab at `~`** running `herdr --session <slug>`, via the `hop`
   skill's `hop-term.py open` (WezTerm). The tab always starts at `$HOME`, so it is
   never tied to a repo that may later be cleaned away.
3. Poll `session list` until the new session reports running.
4. Session-scoped from here on (`herdr --session <slug> ...`): `cd` its pane into the
   worktree, then `agent start <slug> --kind <kind> -- <args>` (Copilot: `--autopilot --allow-all`;
   Claude: `--dangerously-skip-permissions`). If `agent start` will not confirm readiness,
   run the fallback command (`START_AGENT_CMD`, `HOP_AGENT_CMD`, then `coya`/`cla`) in the pane.

**The tab must be a real terminal tab, not `herdr tab create`.** Herdr refuses to nest
("nested herdr is disabled by default"), so a session can only be launched from a pane
that is not itself inside Herdr.

### resume

Only step 2. **No worktree is created and no agent is started** - the session still
holds its own panes, cwd and agent; recreating them would duplicate live work.

### already running

Print the tty and pane and stop. Never a second tab, never a second agent, never a focus
steal - being taken to an existing tab is `hop --focus`, not `start`.

## Safety rules

- **Idempotent by construction.** State is checked before anything is created, so a
  repeated `do <same task>` is a no-op rather than a duplicate stack.
- **Never touch the calling session.** No `cd`, no commit, no stash, no pane close. The
  only writes are a new tab, a new session, and a new worktree.
- Never kill a session, pane, or agent; `start` has no teardown path. Stopping a session is
  `herdr session stop <slug>`, removing a worktree is `wtree clean` - both user-initiated.
- A failed `wtree` step aborts before the tab is opened, so a bad slug cannot leave half
  a stack behind.
- Outside WezTerm, `hop-term.py` cannot open a tab; `start` reports that and stops rather
  than guessing at a terminal.
