# Skills Index

Every skill in `ai-agents/skills/`, grouped by its category folder. This is the human lookup:
when auto-recall misses, scan here and invoke the skill by name. The agent matches intent
against each skill's `description`, not this file, so keep descriptions sharp and each row
here to one line.

## `engineering/`

| Skill | Reach for it when... |
|---|---|
| `review-others` | Review **someone else's** PR, or batch the PRs awaiting my review. |
| `jira-create` | File agent-optimized JIRA tickets. |
| `template-general-readout` | Skeleton for a readout: strategy, launch, GA, research, program review, postmortem. |
| `self-assessment` | Reframe **my own** work against the career principles. |
| `peer-feedback` | Write feedback about **a colleague**. |
| `worth-it` | Pressure-test a project, idea, or area to own **before or during** the work: real impact, Staff-level opportunity, who owns what, how deep I go. |
| `domain-drill` | Learn, map, or teach back a technical domain at staff depth. |
| `sysdesign-drill` | Do a timed, interview-condition system-design rep (not a study session). |
| `study-dashboard` | Build a durable, visual study artifact (HTML dashboard with diagrams, FAQ practice tab, question bank, cross-device progress), not a live drill. |
| `local-server` | Start, stop, or check a local server for personal HTML files. |

## `general/`

| Skill | Reach for it when... |
|---|---|
| `skill-auditor` | Create, refactor, review, or audit a skill, `AGENTS.md`, or `CLAUDE.md` against rules and guardrails; decide if a skill is needed or should merge. |
| `slack-msg` | Draft or reword a short message I'm about to **send**. |
| `dict` | Save or look up vocabulary, polish **my own** English or a draft prompt, or practice a workplace conversation scenario. |
| `html-report` | Build a self-contained HTML page a human reviews to decide something (plan, validation, status).
| `file-layout` | Decide where a file goes, set up a personal or coding project, tidy Downloads or Desktop, or archive old material on a work or personal Mac. |

## `experimental/`

Never installed: `./install.sh` skips this folder and removes links an earlier install made.
Move a skill to another category to install it.

| Skill | Reach for it when... |
|---|---|
| `start` | Kick off a new task: workspace, worktree, and agent in one go. |
| `wtree` | Create, list, show, or clean git worktrees under `$WTREE_ROOT` (default `~/.worktree`). |
| `hop` | Jump to the terminal tab for a worktree, repo, or directory. |
| `yell` | See every running coding-agent session and which need me. |
| `tech-domain-dashboard` | Find the genuinely hard sub-problems in a domain, fact-check them, and build a paired markdown + HTML practice dashboard. |

## Boundaries that trip auto-recall

- **`self-assessment` vs `peer-feedback`**: about me vs about someone else.
- **`worth-it` vs `self-assessment`**: decide what to own and how deep to go on work ahead vs reframe an artifact about work already done.
- **`dict` vs `slack-msg`**: practice on my own English vs an outgoing message I'll send to a person.
- **`study-dashboard` vs `tech-domain-dashboard`**: both build an HTML study dashboard. `study-dashboard` also builds question banks and adds FAQ tabs to an existing file; `tech-domain-dashboard` starts from the hard-sub-problem filter and always fact-checks before the HTML build.
- **`yell` vs `wtree show`**: live agent sessions now vs the worktrees of one repo group.

## Maintenance

- New skill = `<category>/<name>/SKILL.md`, a row here in the same change, then `./install.sh`.
  Agents load skills from one flat directory, so skill names must be unique across categories;
  the installer fails on a duplicate.
- To retire a skill, delete its folder and re-run `./install.sh`; dangling links are pruned.
- `tests/run.sh` must pass before committing; it lints every skill with `skill-auditor`'s
  `spec_check.py`.
