---
name: git-pull
kind: orchestrator
description: "Pull latest from remote for all local git repos under configured roots, dispatched to subagents 5 repos each, with safe branch handling, dirty-repo protection, and SSH-throttle avoidance. Use when: pull latest, pull all repos, update repos, git pull all, sync repos, pull."
---

# Pull Latest Across Local Repos

Pulls latest for every git working tree under the configured roots, **dispatched to
subagents (5 repos per agent)**, then prints one aggregated summary.

## Roots

Default roots come from `DOTFILES_REPO_ROOTS`, a colon- or space-separated list. When it
is unset, discovery uses `$HOME/project`. Override by passing dirs as args (for example,
"pull ~/project" → only that root). If the user names specific roots, use those instead
of the defaults.

## Safety rules (never violated)

Read-mostly. The skill **never** switches branches, force-pulls, stashes, or resets.

| Situation | Action | Status |
|-----------|--------|--------|
| Local changes (`git status --porcelain` non-empty) | **Do nothing** - no fetch, no pull. List the changed files. | `DIRTY` |
| No upstream / upstream deleted on remote (e.g. `[gone]`) | `git fetch --prune` only. Never switch branches. | `SKIPPED` |
| Clean, upstream exists | `git pull --ff-only` (retry/backoff on SSH throttle) | `UPDATED` / `UP-TO-DATE` |
| Non-ff divergence or other error | Report, do not force | `FAILED` |

## Workflow

All helper scripts live in `scripts/` next to this file. Resolve `SKILL_DIR` as the
directory containing this `SKILL.md`.

### Step 1 - Enable SSH multiplexing (throttle avoidance)

Parallel git-over-SSH from one host triggers GitHub rate-limiting
(`Connection reset by 140.82.112.3` / `kex_exchange_identification`). Run once up
front so all agents reuse a single pooled connection:

```bash
"$SKILL_DIR/scripts/setup-ssh-mux.sh"
```

Idempotent - safe to run every time.

### Step 2 - Discover repos

```bash
"$SKILL_DIR/scripts/discover-repos.sh" [ROOT ...]   # defaults to the two roots
```

Prints one absolute working-tree path per line. Handles flat and nested layouts, and
excludes nested sub-clones (for example, `config/external`).
Capture the list; note the total count.

### Step 3 - Batch into groups of 5

Split the discovered paths into consecutive batches of **5** (last batch may be
smaller).

### Step 4 - Dispatch one subagent per batch

Launch the batches **in parallel** using the Task tool (`task` agent type) - put all
batch dispatches in a **single message** so they run concurrently. Each agent's job
is trivial and deterministic:

> Run this exact command and return its stdout verbatim, nothing else:
> `"$SKILL_DIR/scripts/pull-repos.sh" <path1> <path2> ... <path5>`
> Do not modify any repo yourself; the script does all the work. Each output line is
> `STATUS<TAB>path<TAB>detail`.

Pass absolute paths. Each agent pulls its 5 repos serially; parallelism is across
agents (kept safe by the shared SSH connection from Step 1).

> Scale note: for very large repo counts, cap concurrent agents (e.g. ~6–8 batches in
> flight) to stay friendly to the host and remote; queue the rest.

### Step 5 - Aggregate and report

Collect every `STATUS\tpath\tdetail` line from all agents. Print one summary:

- **Tally line:** `N updated · M up-to-date · K skipped · D dirty · J failed`
- **Updated** - list repos (brief).
- **Dirty** - list each repo **and its changed files** (from the detail field) so
  nothing is silently skipped.
- **Skipped** - list each repo + reason (no upstream / upstream gone).
- **Failed** - list each repo + reason.

Lead with anything needing the user's attention (dirty / failed), then the counts.

## Notes

- Re-running is always safe and idempotent.
- A repo on a feature branch with a live upstream **is** pulled (ff-only) - only
  gone/missing upstreams are skipped.
- Repo-group dirs that are not themselves repos are handled automatically - discovery
  keys off `.git`, not directory depth.
