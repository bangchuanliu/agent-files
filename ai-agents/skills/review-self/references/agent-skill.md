# Agent Skill / Command / Plan Review

Review checklist for changes under `.claude/` directories (skills, commands, rules) and `plans/` directories.

---

## File Classification

| Type | Location | Format |
|------|----------|--------|
| **Skill** | `.claude/skills/<name>/SKILL.md` | YAML frontmatter + markdown body |
| **Command** | `.claude/commands/<name>.md` | Markdown (no frontmatter required) |
| **Rule** | `.claude/rules/<name>.md` | Markdown conventions/guidelines |
| **Plan** | `plans/features/<name>/plan.md` | Structured implementation plan |
| **Plan State** | `plans/features/<name>/state.json` | Phase tracking JSON |

---

## Review Checklist

### 1. Skill Review (P0/P1)

#### 1.1 Frontmatter (P0)

Every `SKILL.md` must have valid YAML frontmatter:

```yaml
---
name: skill-name
description: "Clear description of what the skill does and when to trigger it."
---
```

**Check**:
- P0: `name` and `description` are required - skill won't register without them
- P1: `description` should include trigger conditions (when to use), not just what it does
- P1: `description` should be specific enough to avoid false triggers but broad enough to catch real use cases

#### 1.2 Structure (P1)

```
skill-name/
├── SKILL.md           # Required - main instructions
├── references/        # Optional - loaded on demand
│   └── domain.md
├── scripts/           # Optional - executable helpers
└── assets/            # Optional - templates, icons
```

**Check**:
- P1: SKILL.md should stay under ~500 lines - move large content to `references/`
- P1: Reference files should have clear pointers from SKILL.md about when to read them
- P2: Large reference files (>300 lines) should include a table of contents

#### 1.3 Content Quality (P1/P2)

- **P1**: Instructions should use imperative form ("Run X", "Check Y"), not passive voice
- **P1**: Include concrete examples - code snippets, sample commands, expected output
- **P1**: Explain the *why* behind instructions, not just the *what* - LLMs reason better with motivation
- **P2**: Avoid excessive MUST/NEVER/ALWAYS - explain reasoning instead
- **P2**: Don't over-specify steps the model can figure out - focus on what's non-obvious

#### 1.4 Triggering (P1)

- **P1**: Skill description should match realistic user phrases (casual, formal, abbreviated)
- **P2**: Include edge cases - what should NOT trigger this skill?

---

### 2. Command Review (P1/P2)

Commands are simpler than skills - they're user-invoked via `/command-name`.

#### 2.1 Format

- **P1**: First line should clearly state what the command does
- **P1**: Include usage examples with sample arguments
- **P2**: Document optional arguments/flags

#### 2.2 Agent Commands

For commands that orchestrate agents (like `pm.md`, `tl.md`, `dev.md`):

- **P1**: Define clear phase transitions and handoff points between agents
- **P1**: State tracking (state.json) should be updated at each phase
- **P1**: Error handling - what happens when a phase fails?
- **P2**: Avoid duplicating logic that exists in skills - reference the skill instead

---

### 3. Plan Review (P1/P2)

Plans in `plans/features/<name>/plan.md` guide implementation.

#### 3.1 Structure

A well-formed plan should include:

```markdown
# Feature Name

## Overview
Brief description of what and why.

## Scope
What's in scope and explicitly out of scope.

## Design Decisions
Key choices and their rationale.

## Affected Components
Files/modules that will change.

## Tasks
Ordered implementation steps with acceptance criteria.
```

**Check**:
- P1: Tasks should be ordered by dependency - not alphabetically or randomly
- P1: Each task should have clear acceptance criteria (how to know it's done)
- P1: Scope should explicitly list what's out of scope to prevent drift
- P2: Design decisions should include alternatives considered and why they were rejected

#### 3.2 State Tracking

`state.json` should reflect actual progress:

- **P1**: Phase status should match reality - don't mark phases complete that aren't
- **P2**: Include timestamps for phase transitions

---

### 4. Rules Review (P2)

Rules in `.claude/rules/` define project conventions.

- **P2**: Rules should be concise - long rules get ignored
- **P2**: Avoid contradicting other rules or CLAUDE.md
- **P2**: Rules should be actionable, not aspirational

---

### 5. Simplification Review (P1/P2)

Evaluate whether instructions can be tightened without losing clarity or correctness. Apply to SKILL.md, commands, and reference files.

#### 5.1 Redundancy (P1)

- **P1**: Same instruction stated in multiple places - consolidate to one location and reference it
- **P1**: Steps that restate what the model already knows (e.g., "use git to commit" without non-obvious flags) - remove or reduce to the non-obvious part
- **P1**: Examples that demonstrate the same thing - keep the most illustrative one, cut the rest

#### 5.2 Verbosity (P1)

- **P1**: Prose that can be replaced by a table or code block - restructure
- **P1**: Multi-sentence instructions where one sentence suffices - tighten
- **P1**: Explanations of *what* without *why* - either add the why or cut the explanation (the model can infer the what from context)

#### 5.3 Misplaced Content (P1)

- **P1**: SKILL.md over ~500 lines - move domain-specific detail to `references/` and add a "read this when" pointer
- **P1**: Inline content that duplicates an existing reference file - replace with a pointer
- **P2**: Reference files over ~300 lines without a TOC - add one or split

#### 5.4 Dead Weight (P2)

- **P2**: Instructions that can never trigger (unreachable conditions, impossible states)
- **P2**: Commented-out or TODO sections with no timeline - remove or file as a real task
- **P2**: Excessive MUST/NEVER/ALWAYS qualifiers - replace with reasoning ("X because Y" > "YOU MUST X")

---

## Review Gates (Auto-Fail)

- Skill missing `name` or `description` in frontmatter
- Command references nonexistent skills or tools
- Plan tasks have circular dependencies
