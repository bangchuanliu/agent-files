---
name: where-are-we
kind: orchestrator
description: "Report every long-running project in flight across days and weeks - one status file per project under ~/.where-are-we, joined to live worktrees, branches, dirty/unpushed git state and PR state, plus plan.md and other in-flight markdown found under ~/.worktree/*/* that no status file has adopted yet. Gives each project a verdict of pick-up / waiting / review / wrap-up / orphan / paused. Use when: where are we, what am I in the middle of, what's still in flight, what did I leave half-done, status of all my projects, what's gone stale, what happened to that migration, pick up where I left off. NOT for: live agent sessions right now (yell), moving to a tab (hop), starting a task stack (start), or creating and cleaning worktrees (wtree)."
---

# where-are-we - what am I in the middle of?

`yell` answers *which agent needs me right now*. `where-are-we` answers the slower
question: **which projects are in flight, and which one has quietly died?**

The unit here is a **project**, not a session and not a worktree. A migration runs for six
weeks, across three worktrees, two branches and four PRs, with no agent alive most of that
time. Nothing else in the toolchain has a place to record that.

## Usage

```bash
"$SKILL_DIR/scripts/where-are-we" [show] [filter] [--json] [--all] [--no-pr]
"$SKILL_DIR/scripts/where-are-we" update <slug> [--status ...] [--next ...] [--note ...]
```

| User says | Run |
|---|---|
| `where are we` / "what am I in the middle of?" | `where-are-we` |
| "quickly, skip the PR lookups" | `where-are-we --no-pr` |
| "what about the migration work?" | `where-are-we migration` |
| "include the finished ones" | `where-are-we --all` |
| "machine-readable" | `where-are-we --json` |
| "record where I got to" | `where-are-we update <slug> --next "..." --note "..."` |

Requires `python3` and `git`; `gh` optional (skipped by `--no-pr`).

## Status files

One markdown file per project at **`~/.where-are-we/<slug>.md`** (`$WAW_ROOT`):

```markdown
---
project: database-migration
status: active          # active | paused | blocked | done
next: re-run the validation diff for the 3 remaining cases
started: 2026-08-01 09:00
updated: 2026-09-19 17:22
branches:
  - owner/database-migration
worktrees:
  - ~/.worktree/example-repo/owner-database-migration
prs:
  - https://github.com/.../pull/812
---

## Why
(one paragraph, for the reader who has forgotten - that reader is you in three weeks)

## Log
- 2026-09-19 17:22 - first validation pass matches; remaining diff is 0.4%
```

Three design choices, and why:

- **Outside every worktree.** A project outlives its worktrees. `wtree clean` deletes a
  worktree the moment its PR merges; if the record lived inside, the project would vanish
  exactly when it was most worth remembering. Instead the file survives and the tool
  reports `orphan`, naming the branch so you can `wtree new` it back.
- **Markdown with YAML frontmatter, not JSON.** The two fields that matter (`status`,
  `next`) are irreducibly human, so the format has to be pleasant to hand-edit - and
  `## Log` gives narrative a home that a JSON schema never would.
- **One file per project, not one shared file.** Several agents in several worktrees write
  concurrently; per-file writes never conflict, and `ls ~/.where-are-we` is the index.

**Only write what cannot be derived.** Branch, dirty count, unpushed commits, last commit
date, worktree existence and PR state are all read live from `git` and `gh` every run - so
they are never wrong and never need maintaining by hand. The file carries intent only.

## Worktree scan

Every directory two levels under `$WTREE_ROOT` (`~/.worktree/<repo>/<branch-flattened>`, see
`wtree`) is inspected. The branch always comes from
`git -C <path> rev-parse --abbrev-ref HEAD` - the path slug is lossy and is never parsed.

**In-flight markdown** in a worktree is either a well-known note name at top level
(`plan.md`, `notes.md`, `todo.md`, `status.md`, `design.md`, `spec.md`) or *any* `.md` that
`git status --porcelain` reports as dirty or untracked, at any depth. Committed, unchanged
repo docs are repo content, not thinking in progress, so they are ignored.

A worktree is linked to a project by an explicit `worktrees:` / `branches:` entry, or by
slug: `~/.worktree/<repo>/owner-skill-tiers` on branch `owner/skill-tiers` matches project
`skill-tiers` (the `$USER` / `$WTREE_BRANCH_PREFIX` owner prefix is stripped). Worktrees
holding notes that no project claims are listed separately, with the `update` command that
would adopt them.

## Verdicts

One per project, and the sort key of the table. First match wins:

| # | Rule | Verdict |
|---|---|---|
| 1 | `status: done` | **done** (hidden without `--all`) |
| 2 | a referenced worktree or branch no longer exists | **orphan** |
| 3 | `status: blocked` | **waiting** |
| 4 | `status: paused` | **paused** |
| 5 | uncommitted or unpushed work in a linked worktree | **pick-up** |
| 6 | any linked PR is open | **waiting** |
| 7 | ≥1 PR and all closed or merged, tree clean | **wrap-up** |
| 8 | no activity for `$WAW_STALE_DAYS` (default 21) | **review** |
| 9 | otherwise | **pick-up** |

Declared intent outranks inferred state (rules 3–4 above rule 5): a human who wrote
`paused` knows something git does not, so a dirty tree is reported in the reason rather
than overriding the verdict.

**Last activity** is the newest of: the `updated:` field, the last commit in each linked
worktree, and the mtime of each linked note. The status file's own mtime counts *only*
when `updated:` is absent - otherwise a stray `touch` would make a dead project look alive.

## RECOMMENDATIONS

Opinions, beyond the literal spec. Items marked **[implemented]** are already in the code.

1. **Keep the hand-written part down to two fields.** **[implemented]** Git and PR state
   answer *what changed and where*; they can never answer *why* or *what next*. So the tool
   derives everything derivable and asks a human for exactly `status` and `next`. Git
   history is a good substitute for a status file's facts and a useless substitute for its
   judgement.
2. **Update at the end of a session, not on a schedule.** **[implemented]** as the `update`
   subcommand, designed for an agent to call as its last act:
   `where-are-we update <slug> --next "..." --note "..."`. Wiring that into a stop hook
   would automate it fully, but hook installation is a user decision that depends on the
   local agent host, so this skill ships the command and not the hook.
3. **Treat `review` as a prompt, never an action.** **[implemented]** A project untouched
   for three weeks is ambiguous between dead and paused, and only the user can say which.
   The tool asks; it never archives anything.
4. **Survive `wtree clean` by design.** **[implemented]** Records live outside worktrees, a
   deleted worktree becomes `orphan` rather than data loss, and the branch name is kept so
   the worktree can be re-cut. A future improvement worth making in `wtree`: have
   `wtree clean` consult `where-are-we --json` and downgrade a worktree whose project is
   `active` to KEEP.
5. **Adopt, do not duplicate.** **[implemented]** A `plan.md` already *is* a status file
   written by hand. Rather than demanding it be rewritten, the tool lists it as unadopted
   and prints the one command that links it to a project.
6. **Do not merge this into `yell`.** Different clocks (minutes vs weeks), different
   lifetimes (process vs project), different failure mode (a forgotten tab vs a forgotten
   month). `yell` should stay a process inventory.
7. **Not yet implemented, deliberately:** deriving a project from PR history alone (too
   noisy across a repository), auto-closing a project when its last PR merges (silently
   losing follow-up work is worse than a stale row), and issue-tracker linkage (`links:`
   holds URLs today; live issue state belongs behind an explicit flag, not in every run).

## Safety rules

- **`show` is entirely read-only.** It runs only `git rev-parse`, `status`, `rev-list`,
  `log`, and `gh pr list`. It never writes git state, never creates or removes a worktree,
  never starts, stops or touches an agent, session, pane or tab.
- **`update` is the single mutation, and it only ever writes one file under `$WAW_ROOT`.**
  It never touches a repo, a worktree, or anything outside that directory. It creates the
  file if absent and preserves the existing body, appending to `## Log` rather than
  overwriting.
- Branches are never parsed out of worktree directory names.
- A missing worktree is reported, never recreated, and never deleted.
- `gh` failure is not evidence: PR state degrades to `none`/`-` and can only make a project
  look *more* in flight, never less.
- All subprocess output is fully buffered before parsing - no producer is piped into a
  short-circuiting consumer, so there is no intermittent SIGPIPE / exit-141 failure.

## Related

- `yell` - which agent session needs me *right now*.
- `hop` - take me to the tab for that worktree.
- `start` - start a new task stack for a project that needs one.
- `wtree` - create and safely clean the worktrees a project runs in.
