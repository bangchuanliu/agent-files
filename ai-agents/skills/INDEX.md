# Skills Index

Every skill in `ai-agents/skills/`, grouped by its category folder. This is the human lookup:
when auto-recall misses, scan here and invoke the skill by name. The agent matches intent
against each skill's `description`, not this file, so keep descriptions sharp and each row
here to one line.

## `engineering/`

| Skill | Reach for it when... |
|---|---|
| `review-others` | Review **someone else's** PR, or batch the PRs awaiting my review. |
| `pr-comments` | Address review comments and failing checks on **my** PR, or watch it until approved. |
| `jira-create` | File agent-optimized JIRA tickets. |
| `template-general-readout` | Skeleton for a readout: strategy, launch, GA, research, program review, postmortem. |
| `self-assessment` | Reframe **my own** work against the career principles. |
| `peer-feedback` | Write feedback about **a colleague**. |
| `domain-drill` | Learn, map, or teach back a technical domain at staff depth. |
| `sysdesign-drill` | Do a timed, interview-condition system-design rep (not a study session). |
| `local-server` | Start, stop, or check a local server for personal HTML files. |

## `general/`

| Skill | Reach for it when... |
|---|---|
| `skill-creator` | Create, refactor, review, or tighten a skill, `AGENTS.md`, or `CLAUDE.md`. |
| `slack-msg` | Draft or reword a short message I'm about to **send**. |
| `html-report` | Build a self-contained HTML page a human reviews to decide something (plan, validation, status).
| `file-layout` | Decide where a file goes, set up a personal or coding project, tidy Downloads or Desktop, or archive old material on a work or personal Mac. |

## `experimental/`

Installed like any other skill; the folder marks them as still changing.

| Skill | Reach for it when... |
|---|---|
| `start` | Kick off a new task: workspace, worktree, and agent in one go. |
| `wtree` | Create, list, show, or clean git worktrees under `$WTREE_ROOT` (default `~/.worktree`). |
| `hop` | Jump to the terminal tab for a worktree, repo, or directory. |
| `yell` | See every running coding-agent session and which need me. |

## Boundaries that trip auto-recall

- **`self-assessment` vs `peer-feedback`**: about me vs about someone else.
- **`pr-comments` vs `review-others`**: feedback on my PR vs reviewing someone else's.
- **`yell` vs `wtree show`**: live agent sessions now vs the worktrees of one repo group.

## Maintenance

- New skill = `<category>/<name>/SKILL.md`, a row here in the same change, then `./install.sh`.
  Agents load skills from one flat directory, so skill names must be unique across categories;
  the installer fails on a duplicate.
- To retire a skill, delete its folder and re-run `./install.sh`; dangling links are pruned.
- `tests/run.sh` must pass before committing; it lints every skill with `skill-creator`'s
  `spec_check.py`.
