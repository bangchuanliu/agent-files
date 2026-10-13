---
name: skill-auditor
description: "Use when: review or audit the global rule files - the core AGENTS.md and the topic rules it indexes (thinking.md, building.md, communicating.md) - for no-ops, duplication, misplaced strength, missing guardrails, or weak index triggers. NOT for: reviewing a single skill (use the skill-auditor skill directly), or editing source code."
---

# Skill Auditor (rules review)

## Objective

Audit the global rule files so every line steers behaviour, each meaning lives in one place, and every topic file is reached by a sharp trigger in the core rule index. The output lets the user decide which edits to make; it does not make them.

## Scope

- The rule files are the core `AGENTS.md` and every topic file in its rule index. Locate them from the rule index in your loaded global instructions; an index entry may be a symlink, so resolve it to the source directory, which also holds `AGENTS.md`. A path the user gives overrides this.
- IF the source directory cannot be found, stop and ask for the path rather than guessing; `CLAUDE.md` and `copilot-instructions.md` are symlinks to the core `AGENTS.md`, so resolve them instead of auditing them as separate files.
- Review the set as a whole as well as file by file: cross-file duplication, a rule sitting in the wrong topic, and index triggers that overlap or miss a branch are in scope.

## Guardrails

- MUST apply the `skill-auditor` skill and load the reference files its table selects for a review (at least `references/review.md` and `references/levers.md`); treat each rule file as an `AGENTS.md`-style document, not a skill.
- MUST stay read-only: report findings and proposed edits, and change files only when the user explicitly asks.
- MUST NOT propose dropping a hard rule or safety boundary to save tokens; flag it as a judgement call instead.
- MUST leave the private overlay (`~/.agents-local/AGENTS.md`) and other private content out of the findings; it is not part of these files.

## Output

As the skill's `references/review.md` specifies, grouped by file, then a short cross-file section. Distinguish verified facts from judgement calls.
