---
name: skill-creator
kind: leaf
description: "Use when: create a new skill, scaffold a SKILL.md, refactor a skill into constraint-first rules and conditional checks, review a skill against the skill checklist, decide whether a skill needs a fixed workflow, or plan a regression evaluation of a skill rewrite. NOT for: line-level writing polish of a skill, AGENTS.md or CLAUDE.md -> use skill-improver."
---

# Agent Skill Creation Guide

A practical standard for designing, reviewing, and refactoring Agent Skills for coding agents such as Claude Code and Codex.

## Core Philosophy

**Constraint-first, workflow-on-demand.** Specify what must be true, not every step the agent must take. Give the agent autonomy to plan while retaining safety, correctness, and verifiability.

- **Rules over recipes:** define boundaries instead of prescribing routine sequences.
- **Outcomes over steps:** specify success criteria and required evidence.
- **Conditional over unconditional:** activate domain-specific checks only when relevant.
- **Verification over verbosity:** never remove essential checks merely to save tokens.
- **Evaluation over intuition:** compare versions on representative tasks.

## Recommended Structure

| Section | Purpose | Required? |
| --- | --- | --- |
| Objective | Task, trigger/scope, and success criteria | Yes |
| Rules | Hard constraints and default preferences | Yes |
| Conditional Checks | Context-dependent checks or mandatory sequences | When applicable |
| Output & Verification | Deliverable format, evidence, and completion checks | Yes |

Use `MUST` / `MUST NOT` for non-negotiable rules, `SHOULD` / `SHOULD NOT` for defaults with reasonable exceptions, and `IF` / `WHEN` for conditional behavior. Avoid repeating global instructions in each skill.

### Constraints vs. Guardrails

- **Constraints** define the conditions or limits under which a task must be performed (scope, format, allowed operations, performance).
- **Guardrails** are safety/integrity-oriented constraints that prevent unacceptable actions or outcomes (secret exposure, unauthorized writes, fabricated evidence).
- In practice, guardrails can be treated as a subset of constraints. **Combine both under `Rules`** unless high-risk work warrants a separate `Safety Guardrails` section.

## When to Specify a Workflow

Default to agent-selected execution steps. Prescribe a sequence only when skipping or reordering steps could compromise correctness, safety, recoverability, or a required external protocol.

| Situation | Recommendation |
| --- | --- |
| Read every file before reviewing | Avoid; inspect relevant files on demand |
| Understand dependencies before changing code | State as a requirement |
| Back up data before destructive migration | Require explicit ordering |
| Run the same long checklist for every review | Make checks conditional on context |
| Test relevant behavior after changes | Require verification; define what to do if tests cannot run |
| Produce many fixed report sections | Keep only sections necessary for the user |

## Lean Skill Template

```markdown
---
name: example-skill
description: Use when [clear trigger]; accomplish [specific task].
---

# [Skill Name]

## Objective
[What this skill does, its scope, and what success looks like.]

## Rules
- MUST [non-negotiable requirement].
- MUST NOT [forbidden action].
- SHOULD [preferred behavior; exceptions allowed].

## Conditional Checks
- IF [condition], THEN [relevant check or action].
- WHEN [high-risk operation], [required order or approval].

## Output & Verification
- Deliver [minimum useful output].
- Verify [critical properties] using [appropriate evidence].
- Distinguish verified facts from assumptions or untested risks.
- State any checks that could not be completed.
```

The YAML frontmatter fields shown are illustrative; validate them against the target agent's current skill specification.

## Example: Code Review Skill

```markdown
# Code Review

## Objective
Find actionable correctness, reliability, performance, and maintainability issues in relevant code changes.

## Rules
- MUST NOT modify source code.
- MUST ground findings in code evidence.
- MUST NOT invent findings or claim tests were run when they were not.
- SHOULD prioritize correctness and material impact over style.
- SHOULD recommend the smallest practical fix.

## Conditional Checks
- IF reviewing Spark, consider shuffle, skew, partitioning, and unnecessary scans where relevant.
- IF reviewing Airflow, consider retries, idempotency, and failure recovery where relevant.
- IF a finding depends on external code, inspect the dependency or label the uncertainty.

## Output & Verification
- For each finding: severity, file/line, impact, evidence, and suggested fix.
- Recheck findings against the actual code.
- Separate confirmed defects from risks needing validation.
- If no actionable findings are found, say so.
```

## Keep Skills Small Without Losing Capability

Use three layers:

1. **Global instructions:** shared rules and communication defaults.
2. **Lean `SKILL.md`:** task-specific objective, rules, triggers, and verification.
3. **On-demand `references/` and `scripts/`:** detailed domain guidance, examples, deterministic checks, or high-risk procedures.

Do not move indispensable rules into optional references unless the skill explicitly requires loading them when relevant. Prefer scripts for deterministic validations instead of long prose instructions.

## Refactoring Existing Skills

1. Identify the skill's actual purpose and measurable success conditions.
2. Extract hard requirements, safety boundaries, and critical checks from existing workflow prose.
3. Convert routine step-by-step directions into outcome-based rules.
4. Retain ordered steps only where order materially affects safety or correctness.
5. Convert broad checklists into context-triggered checks.
6. Move lengthy examples and specialized reference material out of the core file.
7. Deduplicate instructions already present at the global or project level.
8. Confirm that output and verification requirements survived the rewrite.
9. Evaluate the old and new versions before adopting the rewrite.

## Regression Evaluation

Build a small representative suite (e.g., 10–20 tasks), including normal cases, edge cases, and failure modes. Compare old and new skills with the same model, codebase, tools, and task inputs where possible. Repeat nondeterministic tests.

Track:

- **Task success / correctness:** did the skill achieve the intended outcome?
- **Critical miss rate:** were serious defects or mandatory checks missed?
- **Instruction compliance:** were hard rules obeyed?
- **Evidence quality:** are claims grounded and verification honestly reported?
- **Efficiency:** tokens, latency, and unnecessary tool calls.

Do not accept lower token use as a win if correctness or safety degrades materially.

## Skill Review Checklist

- [ ] Clear trigger, scope, and objective
- [ ] Success criteria are observable
- [ ] Hard rules are distinguishable from preferences
- [ ] No redundant global instructions
- [ ] No unnecessary fixed workflow
- [ ] Mandatory ordered operations are preserved
- [ ] Context-specific checks are conditional
- [ ] Output requirements are concise and actionable
- [ ] Verification and uncertainty reporting are explicit
- [ ] Detailed references are available on demand
- [ ] Regression tests show no material quality regression

## Decision Rule

**Keep a directive if removing it materially increases the chance of failure, unacceptable behavior, or an unverifiable result. Otherwise simplify, condition, relocate, or remove it.**
