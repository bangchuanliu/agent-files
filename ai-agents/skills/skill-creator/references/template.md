# Lean Skill Template and Example

## Template

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

The frontmatter fields are illustrative; validate them against the target agent's current skill specification.

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
