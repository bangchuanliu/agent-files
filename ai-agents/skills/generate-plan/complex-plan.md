# Complex Plan Template

Use for features whose triage verdict is `complex` (any dimension is `complex`). The full pipeline runs: tl → dev (parallel groups) → review → pr → qa → monitor → validate.

`## Requirement` / `## Triage` live in `spec.md` (written by triage) and are NOT duplicated here - `plan.md` is a separate file holding only the execution plan. The generate-plan skill copies the routing frontmatter from `spec.md`, fills in the body sections below, and adds the TL frontmatter fields (including `phases:`, which signals "TL-enriched").

---

## Frontmatter

```yaml
---
# copied from spec.md
feature_name: <kebab-case-name>
complexity: complex
needs_qa: <true | false>
route: "<route string from triage - see triage agent's route table>"
ticket: <TICKET-123 or "none">   # resolved by triage, copied from spec.md

# added by generate-plan skill
branch: <user/feature-name>
created: YYYY-MM-DD
phases:
  - "Group A: <one-line summary>"
  - "Group B: <one-line summary>"
  - "Group C: <one-line summary>"
---
```

> The `created:` field is the universal TL-enriched marker (used by an orchestrating pipeline skill's Phase Detection for both routes). The `phases:` list is the complex-route-specific group summary - it has independent value beyond signaling enrichment.

---

## Body Structure

```markdown
# <feature_name>

<!-- Requirement and Triage live in spec.md - do NOT duplicate them here. -->

## Summary
<2-3 sentences: what this change does and why it matters. Distinct from Requirement - Summary is the TL's framing for implementers; the Requirement (in spec.md) is the upstream ask.>

## Acceptance Criteria
1. <criterion from requirement, verbatim or lightly rephrased>
2. ...

<Every criterion in the requirement must appear here. Do not merge or drop any. Mark ambiguous criteria with a `(?)` and a clarification note - do not silently invent an interpretation.>

## Tasks

### Group A: <name - e.g., "Config + generated resources">
Files: `path/one.yml`, `path/two.json`

- [ ] Task A1: <description>
  - File: `path/one.yml`
  - Action: create | modify | delete
  - Details: <fields to add/change, dependencies on other tasks>

- [ ] Task A2: <description>
  - File: `path/two.json`
  - Action: modify
  - Details: <...>

### Group B: <name - e.g., "Core Scala logic">
Files: `src/.../Foo.scala`, `src/.../Bar.scala`

- [ ] Task B1: ...
- [ ] Task B2: ...

### Group C: <name - e.g., "Tests + Airflow DAG">
Files: `src/test/.../FooSpec.scala`, `airflow/dags/foo_dag.py`

- [ ] Task C1: ...
- [ ] Task C2: ...

## Risks
- <Risk 1: data migration / config schema / downstream consumer / perf hot path / compliance>
- <Risk 2: ...>
```

---

## Authoring Guidance

- **Up to 3 groups, distinct files.** No file appears in two groups; same-file tasks share a group. Aim for 2–3 groups roughly equal in task count and risk.
- **Group names describe scope, not order.** Groups run in parallel - Group A is not "first", just "first listed".
- **Within a group, order matters.** Same-group tasks run sequentially in one dev agent; earlier tasks must not depend on later ones.
- **Common starter shapes** (adapt to the actual file set):
  - Group A: Config YAML, generated resources, schema files
  - Group B: Core logic - job classes, models, utilities
  - Group C: Tests, Airflow DAG definitions, integration glue
- **Acceptance Criteria is the contract.** If the requirement has 5 criteria, the plan has ≥ 5 criteria. Map each criterion to ≥ 1 task; cite the criterion number in task details when helpful.
- **Risks are real, not boilerplate.** Skip the section if there are none - don't pad with "code review may catch issues". List concrete failure modes: schema migration on a 50M-row table, dual-write window, downstream consumer in another repository or service, etc.
