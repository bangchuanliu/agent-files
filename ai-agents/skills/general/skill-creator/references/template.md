# Lean Skill Template and Example

## Template

```markdown
---
name: example-skill
description: Use when [clear trigger]; accomplish [specific task].
---

# [Skill Name]

## Objective
[What the skill should accomplish, its scope, and what success looks like.]

## Context & Tools
<!-- Optional: only when the skill needs specific tools, scripts, references, or context. -->
- [Tool, script, or reference]: [what it is for and when to use it].

## Guardrails & Constraints
- MUST [non-negotiable requirement or boundary].
- MUST NOT [forbidden action]; instead [positive target].
- IF [condition], MUST [required check, order, or approval].

## Preferences
- SHOULD [preferred approach; exceptions allowed].
- IF [condition], SHOULD [relevant check or approach].

## Output
- [Minimum information or artifacts the caller needs.]
- Adapt format and detail to the task; impose no structure the caller does not need.

## Verification
- [Task-specific acceptance criterion], shown by [cheapest reliable evidence].
- Distinguish verified facts from assumptions or untested risks; state any check that could not be completed.
```

The frontmatter fields are illustrative; validate them against the target agent's current skill specification. Drop any section the skill has nothing specific to say in.

## Example: Code Review Skill

```markdown
# Code Review

## Objective
Find actionable correctness, reliability, performance, and maintainability issues in relevant code changes.

## Guardrails & Constraints
- MUST NOT modify source code; report fixes as suggestions.
- MUST ground every finding in code evidence.
- MUST NOT invent findings or claim tests were run when they were not.
- IF a finding depends on external code, MUST inspect the dependency or label the uncertainty.

## Preferences
- SHOULD prioritize correctness and material impact over style.
- SHOULD recommend the smallest practical fix.
- IF reviewing Spark, SHOULD consider shuffle, skew, partitioning, and unnecessary scans where relevant.
- IF reviewing Airflow, SHOULD consider retries, idempotency, and failure recovery where relevant.

## Output
- For each finding: severity, file/line, impact, evidence, and suggested fix.
- If no actionable findings are found, say so.

## Verification
- Each finding rechecked against the actual code.
- Confirmed defects separated from risks needing validation.
```
