---
name: wtree
kind: leaf
description: "Use when: create, list, or safely clean git worktrees kept one per branch under WTREE_ROOT - new worktree for a branch cut from origin's default branch, show worktrees with git, PR, and agent-session state, clean worktrees whose PRs are all closed or merged. NOT for: live agent triage (yell), jumping to a tab or existing path (hop), starting a full task stack (start), or deleting merged branches in a normal clone."
---

# wtree - worktree manager

## Objective

Create, list, and safely clean git worktrees, one per branch under `$WTREE_ROOT/<repo-group>/<branch-slug>` (default root `~/.worktree`), so a repo group's main clone never gets checked out to someone else's branch and finished worktrees can be removed without losing work. The scripts in `scripts/` do the work; this skill decides which to run, resolves the repo group they need, and holds the safety gates for deletion.

Success: `new` prints the worktree path on its last line; `show` gives the user one row per worktree plus any registered-but-missing ones; `clean` removes only worktrees that pass every gate below, after the user has confirmed the dry-run table.

## Context & Tools

`SKILL_DIR` is the directory containing this file. Each script's header gives its usage and flags.

| User says | Run |
|---|---|
| `wtree new <branch>`, or a bare argument such as `wtree message-polish` | `"$SKILL_DIR/scripts/wtree-new.sh" <branch> [repo-group]` |
| `wtree show` / `list` / `ls` / `status` | `"$SKILL_DIR/scripts/wtree-show.sh"` (`--no-pr` skips `gh` and is much faster) |
| `wtree clean` | `"$SKILL_DIR/scripts/wtree-clean.sh"` (dry run) |
| `wtree clean --yes` / "actually delete" | `"$SKILL_DIR/scripts/wtree-clean.sh" --yes`, only after the dry run is confirmed |

- `wtree-list.sh` emits one JSON row per worktree and feeds both `show` and `clean`, so gate data is computed one way; `wtree-sessions.py` does the batched agent-session lookup (live `copilot`/`claude` process, Copilot and Claude session stores, tmux).
- `wtree-new.sh` turns a bare branch name into `$USER/<name>` (override the owner with `WTREE_BRANCH_PREFIX`, opt out with `--no-prefix`); a name containing `/` or matching an existing local or remote ref is used verbatim. It fetches, then cuts from `origin/HEAD`, `origin/master`, or `origin/main`; an existing branch is checked out as-is, and a branch already checked out elsewhere returns that path.
- Requires `git`, `jq`, `gh` (authenticated), and `python3`; `sqlite3` and `tmux` are optional.

## Guardrails & Constraints

- MUST resolve the repo group before running `new`, because the scripts take an exact directory name and never guess, and a worktree cut from the wrong repo is expensive to unwind once a branch, session, and agent are built on it:
  - inside a git repo with no repo named, pass none - the script resolves the main clone, even from inside a worktree;
  - a loose name - map it to one exact repo-group directory under `DOTFILES_REPO_ROOTS` (default `$HOME/project`; extend it for the call, e.g. `DOTFILES_REPO_ROOTS="$HOME/project:$HOME/other"`, when the repo lives elsewhere);
  - IF no clear match, use the current repo when inside one; otherwise stop and report the ambiguity with the candidates.
- MUST cut new branches from origin's default branch, leaving the user's current checkout, dirty or not, untouched. Use `--base <ref>` or `--from-current` only when the user asks for that base. IF the script cannot resolve origin's default branch, stop and ask which base to use.
- MUST read a worktree's branch with `git -C <path> rev-parse --abbrev-ref HEAD`, never from the path slug, because the slug replaces `/` with `-` and is lossy.
- **Deletion gates - never relax these.** MUST remove a worktree only when all four pass, which `wtree-clean.sh` enforces:
  1. no active agent session in or under it;
  2. clean tree - no modified or untracked files and no stash for the branch;
  3. no commit that exists on no remote ref (checked against all remotes, since a merged PR's remote branch is usually deleted);
  4. at least one PR for the branch, and every PR `CLOSED` or `MERGED`.
- MUST run `clean` as a dry run first, show the user the full KEEP/REMOVE table, and pass `--yes` only after the user confirms it, because removal is irreversible.
- MUST treat zero PRs as KEEP (a branch with no PR is in-flight work) and a `gh` failure (`pr_unknown`) as KEEP; "no PR found" never means "no PR exists". IF `gh` fails, report it and leave those rows alone.
- MUST delete only through the script's safe path: `git worktree remove` without `--force`, then `git branch -d` (a branch that is not fully merged stays). MUST NOT run `git branch -D`, `git worktree remove --force`, or any change to the main clone; when a gate blocks removal, report the reason to the user instead.
- MUST pass `--allow-local-commits` (overrides gate 3) only when the user explicitly asks after seeing which commits exist on no remote, because those commits are the only copy of that code. `--closed-only` (excludes merged PRs) and `--keep-branch` (keeps the local branch) only narrow what is removed and follow the user's wording.
- IF a required tool is missing or unauthenticated, stop and report it; for `clean`, that never turns into a REMOVE.

## Output

- `new`: the worktree path, the branch actually used (after any `$USER/` prefix), and its base.
- `show`: the script's table as printed, then any prunable worktrees with the fix (`git worktree prune` in the main clone, run only if the user asks).
- `clean`: the KEEP/REMOVE table with reasons; after `--yes`, what was removed and any branch kept.

## Verification

- `new`: the printed path exists and `git -C <path> rev-parse --abbrev-ref HEAD` shows the expected branch.
- `clean --yes`: only rows marked REMOVE in the confirmed dry run are gone, and `wtree-show.sh` no longer lists them.
- State any gate that could not be evaluated (e.g. `gh` unavailable) rather than inferring its result.
