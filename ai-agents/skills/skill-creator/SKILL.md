---
name: skill-creator
kind: leaf
description: "Use when: create a new skill, scaffold a SKILL.md, restructure or refactor a skill into constraint-first rules and conditional checks, review a skill's structure against the skill checklist, decide whether a skill needs a fixed workflow, or evaluate a skill rewrite against the old version. NOT for: line-level wording polish of a skill, AGENTS.md or CLAUDE.md -> use skill-improver."
---

# Skill Creator

**Constraint-first, workflow-on-demand.** A skill specifies what must be true, not every step. The agent plans; the skill keeps it safe, correct, and verifiable. Rules over recipes, outcomes over steps, conditional over unconditional checks, verification over verbosity, evaluation over intuition.

## Objective

Create, review, or refactor an agent skill so it meets this standard. Success means the skill has a clear trigger and observable success criteria, its hard rules survive, the spec check passes, and (for a rewrite) evaluation shows no material regression.

## Rules

- MUST structure the skill as **Objective** (task, scope, success criteria), **Rules**, **Output & Verification**, plus **Conditional Checks** when applicable. [references/template.md](references/template.md) has a template and a worked example.
- MUST write hard rules as `MUST` / `MUST NOT`, defaults as `SHOULD` / `SHOULD NOT`, and context-dependent behavior as `IF` / `WHEN`.
- MUST put constraints (scope, format, allowed operations) and guardrails (secrets, unauthorized writes, fabricated evidence) together under Rules. Add a separate `Safety Guardrails` section only for high-risk work.
- MUST prescribe an ordered sequence only when skipping or reordering steps would compromise correctness, safety, recoverability, or a required external protocol. Otherwise state the outcome and let the agent choose the steps. For example: "back up before a destructive migration" needs an order; "read every file before reviewing" does not.
- MUST keep every rule that is essential to the skill in `SKILL.md`. Detail goes to `references/`, and deterministic checks go to `scripts/`. If the skill relies on a reference, it MUST say when to load it.
- MUST NOT restate global or project instructions.
- MUST NOT drop an existing hard requirement, safety boundary, or critical check to save tokens.
- SHOULD make domain checks conditional on context rather than running them as one long checklist every time.
- SHOULD replace long prose describing a deterministic check with a script.
- SHOULD keep fixed report sections to what the user actually needs.

## Conditional Checks

- IF refactoring an existing skill, first extract its purpose, hard requirements, safety boundaries, and critical checks. Confirm each one survives the rewrite.
- IF refactoring or materially changing a skill, evaluate the new version against the old one before adopting it ([references/evaluation.md](references/evaluation.md)). Do not adopt a rewrite that loses correctness or safety.
- IF the target agent's skill spec differs from this repo's, validate the frontmatter against the target spec.
- IF another skill's description covers the same triggers, sharpen both descriptions with `NOT for:` routing.

## Output & Verification

- Run `python3 ../skill-improver/scripts/spec_check.py --house <skill-dir>` and resolve its findings.
- For a review, report each checklist item below as pass, fail, or partial, with line-level evidence and a suggested fix. Say plainly if nothing needs changing.
- For a create or refactor, deliver the skill files and the spec-check result, plus the evaluation result or a statement that evaluation was not run and why.
- Distinguish verified facts from assumptions. State any check that could not be completed.

**Review checklist:** clear trigger, scope, and objective · observable success criteria · hard rules distinct from preferences · no redundant global instructions · no unnecessary fixed workflow · mandatory ordered operations preserved · context-specific checks are conditional · concise, actionable output requirements · explicit verification and uncertainty reporting · detailed references available on demand · no material regression on evaluation.

**Decision rule:** keep a directive if removing it materially increases the chance of failure, unacceptable behavior, or an unverifiable result. Otherwise simplify it, make it conditional, move it out, or remove it.
