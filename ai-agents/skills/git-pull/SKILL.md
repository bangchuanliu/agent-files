---
name: git-pull
kind: orchestrator
description: "Pull local git repos under configured roots with dirty-repo protection, safe branch handling, ff-only updates, and SSH-throttle avoidance. Use when: pull latest, pull all repos, update repos, git pull all, sync repos, or pull."
---

# Pull Latest Across Local Repos

Pull latest for every git working tree under the configured roots, then print one aggregated summary. Use parallel workers when your host agent supports them; otherwise run the same batch script serially.

## Roots

Default roots come from `DOTFILES_REPO_ROOTS`, a colon- or space-separated list. When it
is unset, discovery uses `$HOME/project`. Override by passing dirs as args (for example,
"pull ~/project" → only that root). If the user names specific roots, use those instead
of the defaults.

## Safety rules

Read-mostly. The helper scripts **never** switch branches, force-pull, stash, or reset.

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

Completion criterion: the script exits 0 and reports multiplexing configured or already configured.

### Step 2 - Discover repos

```bash
"$SKILL_DIR/scripts/discover-repos.sh" [ROOT ...]   # defaults to the two roots
```

Prints one absolute working-tree path per line. Handles flat and nested layouts, and
excludes nested sub-clones (for example, `config/external`).
Capture the list; note the total count. Completion criterion: every line is an absolute path to a top-level git work tree.

### Step 3 - Batch into groups of 5

Split the discovered paths into consecutive batches of **5** (last batch may be smaller). Completion criterion: every discovered path appears in exactly one batch.

### Step 4 - Run one worker per batch

Launch the batches in parallel using the host agent's worker/subagent facility when available. If the host has no such facility, run the batches serially in the current session. Each worker's job is deterministic:

> Run this exact command and return its stdout verbatim, nothing else:
> `"$SKILL_DIR/scripts/pull-repos.sh" "path1" "path2" ... "path5"`
> Do not modify any repo yourself; the script does all the work. Each output line is
> `STATUS<TAB>path<TAB>detail`.

Pass absolute paths. Each agent pulls its 5 repos serially; parallelism is across
workers (kept safe by the shared SSH connection from Step 1).

> Scale note: for very large repo counts, cap concurrent workers (for example, 6 to 8 batches in
> flight) to stay friendly to the host and remote; queue the rest.

Completion criterion: every batch has a captured stdout stream, and every line uses the three-field tab-separated format.

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
