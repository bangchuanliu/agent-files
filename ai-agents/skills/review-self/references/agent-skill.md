# Agent document review

Review checklist for agent-consumed documents: skills, commands, repository rules, and implementation plans.

## Contents

- [Scope](#scope)
- [Skill review](#skill-review)
- [Command review](#command-review)
- [Plan review](#plan-review)
- [Rule review](#rule-review)
- [Review gates](#review-gates)

## Scope

| Type | Common locations | Format |
|---|---|---|
| **Skill** | `*/skills/<name>/SKILL.md` | YAML frontmatter plus markdown body |
| **Command** | host command folders | Markdown instructions |
| **Rule** | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, host rule folders | Markdown conventions |
| **Plan** | `plans/features/<name>/plan.md` or project plan folders | Ordered implementation plan |

For writing-quality levers - context pointers, progressive disclosure, co-location, completion criteria, leading words, positive prompting, and pruning - use `skill-improver` as the single source of truth. This file adds review gates and checklists for applying those levers to agent documents.

## Skill review

### Frontmatter

Check every `SKILL.md`:

- **P0:** frontmatter parses as YAML and contains `name` and `description`.
- **P0:** `name` matches the folder and is lowercase kebab-case.
- **P1:** `kind:` is present and is `leaf` or `orchestrator`.
- **P1:** `description` is a sharp context pointer: leading word first, one trigger per branch, false-trigger route when useful.
- **P1:** host filters such as `agents:` have a portable meaning or the skill gives a portable fallback.

Run the local mechanical checker when this repo provides one, for example:

```bash
python3 ai-agents/skills/skill-improver/scripts/spec_check.py ai-agents/skills/<name>
```

### Body and references

- **P1:** main `SKILL.md` keeps the required sequence in view and pushes branch-only reference behind links.
- **P1:** each step has a checkable completion criterion.
- **P1:** links to references are live, and a referenced file is loaded only when its branch fires.
- **P2:** long reference files have a Contents section or are split by branch.
- **P2:** examples are concrete and few: keep the one that changes behavior.

### Portability

- **P1:** tool-specific instructions name the capability first and the host implementation second. Example: "ask through the host's user-prompt tool; if none exists, stop before the write".
- **P1:** a named agent, slash command, MCP tool, or shell path has a direct fallback.
- **P2:** repository facts come from files or commands instead of cached prose.

## Command review

Commands are normally user-invoked. Check:

- **P1:** first paragraph states the outcome and required inputs.
- **P1:** arguments and flags have examples.
- **P1:** side effects are gated with explicit confirmation when they write outside the user's own branch or workspace.
- **P1:** orchestrated phases have handoff artifacts and failure behavior.
- **P2:** command logic points to shared skills instead of duplicating their rules.

## Plan review

A well-formed plan includes:

```markdown
# Feature Name

## Overview
## Scope
## Design Decisions
## Affected Components
## Tasks
```

Check:

- **P1:** tasks are dependency-ordered.
- **P1:** every task has acceptance criteria or a done condition.
- **P1:** scope lists exclusions that prevent drift.
- **P1:** changed files and validation steps are explicit.
- **P2:** design decisions include important alternatives and why they were rejected.
- **P2:** state-tracking files match actual progress when present.

## Rule review

Rules define conventions. Check:

- **P2:** concise, actionable wording.
- **P2:** no contradiction with higher-priority rules.
- **P2:** project-specific facts live in project files, not global rules.

## Review gates

Auto-fail the review when any is true:

- Skill frontmatter is missing or unparsable.
- Command or skill points to a nonexistent required file, skill, command, or tool without fallback.
- Plan tasks have circular dependencies or no completion criteria.
- Instructions require one host agent's feature with no portable fallback.
