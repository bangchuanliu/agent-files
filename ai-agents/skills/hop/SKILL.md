---
name: hop
kind: orchestrator
description: "Hop: resolve a branch, worktree, repo checkout, or directory to its path and terminal tab; report an existing tab/agent, focus it, or open/resume a tab. Use when: hop, go to, goto, switch worktree, jump to branch, open tab for this branch, is there a tab for this worktree, take me there. NOT for: starting a task stack with worktree + Herdr + agent (start), live agent triage (yell), long-horizon project status (where-are-we), or creating/cleaning worktrees (wtree)."
---

# hop - find or open the terminal tab for a directory

**An agent cannot change your shell's directory**, so hop works at the *terminal tab*
level: it finds a tab already sitting in the destination (and which agent is running in
it), or opens a new tab there and starts the configured agent command.

**The current session is left completely alone**, and hop never touches git state - no
commit, no stash, no checkout. Worktrees are independent checkouts, so moving between
tabs disturbs nothing.

## Usage

```bash
"$SKILL_DIR/scripts/hop.sh" <branch-or-dir> [flags]
```

| User says | Run |
|---|---|
| `hop <branch>` / "switch to X" | `hop.sh <branch>` |
| "jump me there" | `hop.sh <branch> --focus` |
| "open another tab anyway" | `hop.sh <branch> --new-tab` |
| "open it but don't yank my focus" | `hop.sh <branch> --no-focus` |
| "start tmux there instead" | `hop.sh <branch> --tmux` |
| "just the path, don't touch my terminal" | `hop.sh <branch> --no-term` |

Flags: `--focus`, `--no-focus`, `--new-tab`, `--tmux`, `--no-agent`, `--cmd <shell-cmd>`,
`--no-term`, `--repo-group <name>`.

`--focus` and `--no-focus` are about different tabs: `--focus` jumps to an **existing**
tab, `--no-focus` stops a **newly opened** one from grabbing the screen - which is what
`yell` uses when it reopens several at once.

## Order of operations

1. **Resolve**, first match wins:
   1. an existing directory path
   2. a worktree under `$WTREE_ROOT` whose **checked-out branch** equals the argument
      (or ends in `/<argument>`, so `message-polish` finds `banliu/message-polish`)
   3. a worktree **directory name** under `$WTREE_ROOT/*/`
   4. a repo checkout under any configured root at one or two levels deep

   Roots come from `DOTFILES_REPO_ROOTS`, a colon- or space-separated list that
   defaults to `$HOME/project`. Nothing resolves? hop
   stops and points at `wtree show` / `start <name>`; it does not create anything.
2. **Terminal** - find tabs already in the destination and report them with any running
   agent, or open a new tab there and start the agent command.

## Terminal tabs

`scripts/hop-term.py` drives this, via `wezterm cli` (exact per-pane cwd and tty):

```bash
hop-term.py find  <dir>            # JSON: tabs at/under dir, agents running in each
hop-term.py open  <dir> --cmd CMD  # new tab at dir, runs CMD, focuses it
hop-term.py focus <pane-id>
```

**Agent detection is two-layered, because Herdr hides its agents.** A bare agent is found
by matching the pane's `tty_name` against `ps -t`, so the tab counts as busy only when a
real `copilot`/`claude` process is attached to it. But in a Herdr-managed tab the tty's
process is `herdr` - the agent lives inside Herdr's own pty and is invisible to `ps -t`.
So when `herdr` is on the tty, hop reads the session name off its command line and asks
`herdr [--session <name>] agent list` for the truth, reporting the agent **and its
lifecycle status**:

```
pane 44  AGENT RUNNING (copilot:working) [herdr:code-review]  banliu-code-review
```

Without this, every tab created by `start` would look empty. Tabs running `tmux` are still
flagged `in_tmux`, since the agent may live inside the terminal multiplexer.

**Tab matching is also two-layered, for the same reason.** A tab opened by `start` stays at
`$HOME` - the worktree lives in the Herdr session *inside* it, not in the WezTerm pane's
own cwd. So when a tab hosts Herdr, hop also matches the session's pane cwds against the
destination. Without this, hop would decide a `start`-created task had no tab and open a
duplicate on top of the running agent. `cwd` reports the matched worktree; `tab_cwd`
reports the WezTerm pane's own cwd.

**Default behaviour when a tab already exists: report, do not switch.** You get the pane
id, the title, and what is running, then hop stops - it never steals focus from or
duplicates a session you are already using. `--focus` opts into jumping (it prefers a
pane that already has an agent); `--new-tab` opts into a second tab.

When no tab exists, hop opens one. What it runs there depends on what it finds:

- **A live Herdr session at the destination** - hop runs `herdr --session <name>` and
  resumes it. Closing a tab does not kill a Herdr session: the session, its cwd and its
  agent all survive. Starting a fresh agent would strand the original and leave two
  agents on one worktree, so hop resumes instead.
- **Nothing there** - hop runs `$HOP_AGENT_CMD`, defaulting to the installer alias for
  whichever agent CLI is on PATH (`coya` for Copilot CLI, else `cla` for Claude Code).

Use `--tmux` for `tmux new-session -A -s <dir>`, `--no-agent` for a bare shell, or
`--cmd` for anything else - all three bypass the resume path.

```bash
hop-term.py herdr-session-for <dir>   # name of a live Herdr session at/under dir
```

Non-WezTerm terminals are not driven automatically: hop reports that it could not open
a tab and prints the `cd` command instead. Point `WEZTERM_BIN` at the binary if yours
lives elsewhere.

### Shell function (optional)

For plain `cd`-in-place behaviour without the tab machinery:

```bash
echo "source $SKILL_DIR/scripts/hop-shell-init.sh" >> ~/.zshrc
```

Then `hop <branch> --no-term` cds the current shell; the destination path is always the
last line of stdout, with all commentary on stderr.

## Safety rules

- **Never modify git state.** hop only reads (`rev-parse`, `status`). It does not
  commit, stash, checkout, or create branches or worktrees.
- **Do nothing to the current session.** No cd, no pane close - the tab you are in is
  left exactly as it was.
- **Never hijack a live session.** If a tab already exists, report it and stop; only
  `--focus` may move the user, and only `--new-tab` may open a duplicate.
- **Never start a second agent on a worktree that already has one.** A detached Herdr
  session still owns its agent, so hop resumes the session rather than launching a rival
  agent beside it.
- Never kill a pane, a tmux session, a Herdr session, or an agent process.
