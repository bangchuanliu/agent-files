# Skills Index

Every skill in `ai-agents/skills/`, grouped by **intent** (what I'm trying to do). This is the
human lookup: when auto-recall misses, scan here and invoke the skill by name. The agent
matches intent against each skill's `description`, not this file, so keep descriptions sharp
and each row here to one line.

## Learn & drill

| Skill | Reach for it when... |
|---|---|
| `domain-drill` | Learn, map, or teach back a technical domain at staff depth. |
| `sysdesign-drill` | Do a timed, interview-condition system-design rep (not a study session). |

## Career writing

| Skill | Reach for it when... |
|---|---|
| `self-assessment` | Reframe **my own** work against the career principles. |
| `peer-feedback` | Write feedback about **a colleague**. |
| `slack-msg` | Draft or reword a short message I'm about to **send**. |
| `template-general-readout` | Skeleton for a readout: strategy, launch, GA, research, program review, postmortem. |
| `template-doc-data-issue-rc` | Write or review a data investigation / RCA write-up. |

## Code review & planning

| Skill | Reach for it when... |
|---|---|
| `review-self` | Review **my own** diff before a PR, or triage comments left on my PR. |
| `review-others` | Review **someone else's** PR, or batch the PRs awaiting my review. |
| `generate-plan` | Turn a triaged `spec.md` into an execution `plan.md`. |
| `skill-improver` | Write, audit, or tighten a skill, `AGENTS.md`, or `CLAUDE.md`. |
| `jira-create` | File agent-optimized JIRA tickets. |

## Worktrees, terminals & sessions

| Skill | Reach for it when... |
|---|---|
| `start` | Kick off a new task: workspace, worktree, and agent in one go. |
| `wtree` | Create, list, show, or clean git worktrees for a repo group. |
| `hop` | Jump to the terminal tab for a worktree, repo, or directory. |
| `yell` | See every running coding-agent session and which need me. |
| `where-are-we` | Status of every long-running project across days and weeks. |
| `git-pull` | Pull latest for all local repos under my roots. |

## Data checks (source vs target)

| Skill | Reach for it when... |
|---|---|
| `table-row-count` | Compare row totals. |
| `table-schema-check` | Detect schema drift. |
| `table-null-check` | Null rate per critical column. |
| `table-duplicate-check` | Uniqueness by natural key. |
| `table-distribution-check` | Category drift or top-N reshuffle in a column. |
| `table-freshness-check` | Latest partition on time and complete. |
| `table-traceability-check` | Orphans, coverage, field-level integrity. |

## Personal infra

| Skill | Reach for it when... |
|---|---|
| `gsheet` | Read or write a Google Sheet from the terminal. |
| `local-server` | Start, stop, or check a local server for personal HTML files. |
| `docs-preview` | Build and serve a Docusaurus site locally. |
| `file-organization` | Decide where a file belongs, name it, or tidy a directory. |

## Boundaries that trip auto-recall

- **`self-assessment` vs `peer-feedback`**: about me vs about someone else.
- **`review-self` vs `review-others`**: whose PR it is.
- **`yell` vs `where-are-we` vs `wtree show`**: live agent sessions now vs projects across
  weeks vs the worktrees of one repo group.

## Maintenance

- New skill = new dir with a `SKILL.md`, a row here in the same change, then `./install.sh`.
- Parked skills live in `ai-agents/experimental/` and are not installed.
- `tests/run.sh` must pass before committing; it lints every skill with `skill-improver`'s
  `spec_check.py`.
