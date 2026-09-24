# Personal Skills Index

My own skills, grouped by **intent** (what I'm trying to do), not by topic. This is the
human lookup — when auto-recall misses, scan here and invoke the skill explicitly with
`/<name>`. Work skills (`attribution-*`, `qa-*`, `data-*`, `commit-pr`, …) are **not**
listed here; find those with `li-plugin-tool:recommend` ("is there a skill for X?").

> The agent matches your intent against each skill's `description`, not against this file.
> This index is for *you*. Keep descriptions sharp; keep this list short.

## 🎓 Learn & drill — deliberate practice

| Skill | Reach for it when… |
|-------|--------------------|
| `domain-drill` | I want to learn / map / teach-back a technical domain at staff depth (Socratic L1→L6). |
| `sysdesign-drill` | I want a timed, interview-condition system-design rep — not a study session. |
| `dict` | Vocabulary capture, polishing my *own* English as a learner, prompt-polish, or workplace conversation practice. |

## ✍️ Career writing — raw work → polished artifact

| Skill | Reach for it when… |
|-------|--------------------|
| `self-assessment` | Reframe **my own** work against the 11 career principles, highlight quantified impact. |
| `peer-feedback` | Write feedback about **a colleague** (the person) — Strengths / Growth / Development. |
| `slack-msg` | Draft or reword a short, polite message I'm about to **send** to a coworker. |

## 🛠 Personal infra — tools the other skills lean on

| Skill | Reach for it when… |
|-------|--------------------|
| `local-server` | Start/stop/check the tiny local HTTP server that serves & saves my HTML data files. |
| `file-organization` | Decide where a doc/file belongs, name it, or clean up a messy directory (lifecycle taxonomy). |

## Boundaries that trip auto-recall

- **`dict` vs `slack-msg`** — both touch "rewrite my text." `dict` = practice on **my own English**
  (I'm the learner). `slack-msg` = an **outgoing message** I'll send. If it ships to a person, it's `slack-msg`.
- **`self-assessment` vs `peer-feedback`** — `self-assessment` is about **me**; `peer-feedback` is about
  **someone else**. Self vs other is the dividing line.

## Maintenance

- Audit descriptions with `skill-improver` when recall feels off or after adding a skill.
- New skill = new dir under `ai-agents/skills/` with a `SKILL.md`; the root `./install.sh`
  (via `.claude/install.sh` / `.copilot/install.sh`) auto-discovers and symlinks it.
  Add a one-line row here in the same change.
