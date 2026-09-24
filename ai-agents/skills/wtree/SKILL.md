---
name: wtree
kind: orchestrator
description: "Manage git worktrees for repo groups under the per-group worktree root, with agent-session awareness. Modes: show (every worktree + its live Copilot/Claude/tmux sessions, git state and PR state), clean (remove only worktrees with no active session, no local work and an already closed/merged PR), new (cut a fresh worktree from origin's default branch, safe to run from a dirty feature branch). Use when: wtree, worktree, git worktree, list worktrees, clean worktrees, new worktree, worktree sessions, new branch off master. NOT for: pulling latest across normal clones (git-pull), or deleting merged branches inside a normal clone."
---

# wtree - worktree manager

One worktree per branch, all under a single root, so the main clone for a repo group is
never checked out to someone else's branch.

## Layout

```
~/.worktree/<repo-group>/<branch-with-/-replaced-by->
  e.g. ~/.worktree/example-service/banliu-login-fix   (branch banliu/login-fix)
```

Exactly two levels deep, so `~/.worktree/*/*` enumerates everything. The path slug is
**lossy**: never parse a branch back out of it. Always read the branch with
`git -C <path> rev-parse --abbrev-ref HEAD`.

Configuration:

- `WTREE_ROOT` defaults to `~/.worktree`.
- `DOTFILES_REPO_ROOTS` is a colon- or space-separated list of main-clone search roots.
  It defaults to `$HOME/project`.

**`wtree` does not infer which repo group you mean.** Given a repo group name it looks under
`DOTFILES_REPO_ROOTS`; given nothing it uses the current git repo; otherwise it errors.
Guessing needs the conversation, so it belongs to the caller - see the "Which repo"
section of the `start` skill. Keep this script mechanical and predictable: a worktree
cut from the wrong repo is expensive to unwind, because a branch, session and agent get
built on top of it.

A repo outside the default `$HOME/project` root must be covered by `DOTFILES_REPO_ROOTS`,
e.g. `DOTFILES_REPO_ROOTS="$HOME/project:$HOME/other" wtree-new.sh <branch> my-repo`.

## Modes

`SKILL_DIR` = the directory containing this file.

| User says | Run |
|---|---|
| `wtree show` (aliases: `list`, `ls`, `status`) | `"$SKILL_DIR/scripts/wtree-show.sh"` |
| `wtree clean` | `"$SKILL_DIR/scripts/wtree-clean.sh"` (dry run) |
| `wtree clean --yes` / "actually delete" | `"$SKILL_DIR/scripts/wtree-clean.sh" --yes` |
| `wtree new <branch>` | `"$SKILL_DIR/scripts/wtree-new.sh" <branch> [repo-group]` |

A bare argument with no mode word (e.g. `wtree message-polish`) means `new <branch>`.

Resolve the repo group before calling any script. Scripts take the exact directory name.
When the user gives a loose name, use local repo knowledge or the configured roots to pick
one exact repo group name. If there is no clear match, prefer the current repo when inside
one; otherwise report the ambiguity.

`wtree-new.sh` itself prefixes a bare branch name with `$USER/` to match the
`<user>/<topic>` convention - `message-polish` becomes `banliu/message-polish`. A name
that already contains a `/`, or that matches an existing local or remote ref, is used
verbatim. Override the owner with
`WTREE_BRANCH_PREFIX`, or opt out with `--no-prefix`.

Shared flags: `--repo-group <name>` to scope to one repo group, `--idle-mins N` (default
30) for the session-liveness window. `show` also takes `--json` and `--no-pr` (skip `gh`,
much faster).

### new

Safe to run from anywhere, including a dirty worktree on a feature branch. The current
checkout is never used as the base:

1. The repo group is resolved from the cwd (hopping from any worktree back to its main
   clone via `--git-common-dir`), or from an explicit repo-group argument.
2. `git fetch --prune origin` in the main clone.
3. Base = `origin/HEAD` -> `origin/master` -> `origin/main`, first that resolves. If none
   resolve it errors out rather than silently branching off your current HEAD.
4. `git worktree add -b <branch> <path> <base>` from the main clone, so your dirty tree is
   never touched, stashed, or switched.

Existing branches short-circuit step 3: a local branch is checked out as-is, a remote-only
branch is created with `--track`. If the branch is already checked out in another
worktree, the existing path is printed instead of failing.

Flags: `--base <ref>` to branch from something else, `--from-current` to branch from the
current HEAD (mutually exclusive with `--base`), `--no-prefix` to skip the `$USER/`
branch-name prefix.

### show

Prints one row per worktree: repo group, branch, git state (`clean` / `dirty(n)` / `stash(n)` /
`ORPHAN` / `DETACHED`), ahead/behind upstream, PR state, active agent sessions, last
session activity, path. Then lists worktrees git still has registered but whose directory
is gone (fix with `git worktree prune` in the main clone).

### clean

Removes a worktree **only** when every gate passes:

| # | Gate | Source |
|---|------|--------|
| 1 | no active agent session | Copilot + Claude + tmux, see below |
| 2 | clean tree - no modified, no untracked, no stash for the branch | `git status --porcelain`, `git stash list` |
| 3 | nothing would be lost - no commit that lives on no remote ref | `git rev-list --count HEAD --not --remotes` |
| 4 | at least 1 PR for the branch and **every** PR is `CLOSED` or `MERGED` | `gh pr list --head <branch> --state all` |

Then: `git worktree remove` -> `git worktree prune` -> `git branch -d` (safe delete only;
on failure the branch is kept) -> `rmdir` the empty `~/.worktree/<repo-group>` dir.

**Hard safety rules - never relax these:**

- **Dry run is the default.** Only `--yes` deletes anything. Always show the user the
  KEEP/REMOVE table first and let them confirm.
- **Zero PRs means KEEP.** A branch with no PR is in-flight work, not garbage.
- **`gh` failure means KEEP.** The row is marked `pr_unknown` and fails closed; never assume
  "no PR found" means "no PR exists".
- Never `git branch -D`, never `worktree remove --force`, never touch the main clone.
- `--closed-only` narrows gate 4 to `CLOSED` (excludes merged PRs).
- `--keep-branch` removes the worktree but leaves the local branch.
- `--allow-local-commits` overrides gate 3. A merged PR normally has its remote branch
  deleted, which is why gate 3 checks *all* remote refs rather than `@{u}` - merged work
  is still reachable from the default branch. A branch whose commits are on no remote at all
  is the only copy of that code, so it is kept unless you pass this flag.

## Agent-session detection

A worktree counts as ACTIVE if any of these hold (window = `--idle-mins`, default 30):

- **Running process** (authoritative) - a live `copilot` or `claude` process whose `lsof`
  cwd is at or under the worktree. This is the only signal that is always correct: the
  Copilot session store is written lazily, so a session running *right now* may not be in
  it yet. Override the process names with `WTREE_AGENT_COMMS=copilot,claude,...`.
- **Copilot CLI** - a session id in `~/.copilot/open-sessions-state.json` with
  `working: true` or a `refreshedAt` inside the window, whose cwd (from
  `~/.copilot/sidebar-sessions-state/<sha256-of-cwd>.json`, falling back to
  `session-store.db`) is at or under the worktree.
- **Claude Code** - `~/.claude/projects/<path with / and . replaced by ->/` contains a
  `*.jsonl` modified inside the window.
- **tmux** - a pane whose `pane_current_path` is at or under the worktree and whose
  command looks like an agent.

The DB is opened read-only with `immutable=1`, so a running agent's WAL lock can never
block or corrupt the read.

## Scripts

```
scripts/wtree-new.sh       create or reuse a worktree cut from origin's default branch;
                           prints the path on the last line
scripts/wtree-list.sh      one JSON object per worktree (shared by show and clean)
scripts/wtree-show.sh      human table + prunable-worktree report
scripts/wtree-clean.sh     gate evaluation, dry run by default
scripts/wtree-sessions.py  batched path -> active-session lookup
```

`show` and `clean` both read `wtree-list.sh`, so the gate data is computed exactly one way.

Requires `git`, `jq`, `gh` (authenticated), `python3`; `sqlite3`/`tmux` optional.
