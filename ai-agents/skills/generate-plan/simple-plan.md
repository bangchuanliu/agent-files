# Simple Plan Template

Use for features whose triage verdict is `simple` (every dimension is `simple`). Implement directly from this plan; no parallel groups, no TL review of QA/monitor/validate phases.

Also used for `complexity: tiny` - keep tasks to allow-listed drop-in edits (no new branches/predicates/public APIs/schema changes).

`## Requirement` / `## Triage` live in `spec.md` (written by triage) and are NOT duplicated here - `plan.md` is a separate file holding only the execution plan. The generate-plan skill copies the routing frontmatter from `spec.md` and fills in the body sections below.

---

## Frontmatter

```yaml
---
# copied from spec.md
feature_name: <kebab-case-name>
complexity: simple
needs_qa: <true | false>
route: "<route string from triage - see triage route table>"
ticket: <TICKET-123 or "none">   # resolved by triage, copied from spec.md

# added by generate-plan skill
branch: <user/feature-name>
created: YYYY-MM-DD
---
```

> No `phases:` field - simple plans have a single linear task list.

---

## Body Structure

```markdown
# <feature_name>

<!-- Requirement and Triage live in spec.md - do NOT duplicate them here. -->

## Summary
<2-3 sentences: what this change does and why. Stays focused; simple plans don't need acceptance-criteria expansion if the requirement is already concrete.>

## Tasks

- [ ] Task 1: <description>
 - File: `path/to/file`
 - Action: create | modify | delete
 - Details: <specific changes - fields, methods, config keys>

- [ ] Task 2: <description>
 - File: `path/to/other-file`
 - Action: modify
 - Details: <...>

<Order tasks by dependency. A simple plan typically has 1–4 tasks; if it grows past 6, reconsider the triage verdict.>

## Risks
- <Anything that could block completion or surprise reviewers - typically empty or one item for simple plans.>

## Constraints

<!-- Required for `complexity: tiny` (allow-listed drop-in edits + block-on-scope-expansion rule).
     Omit this section for plain simple plans. -->

**Allowed change kinds (drop-in edits only):**
- Doc / comment / changelog edit
- Log-message text edit
- Constant value tweak (in code with existing test coverage)
- Compiler-verified rename, including public methods when grep + compiler confirm in-repo coverage
- Dead-code removal
- YAML / config value-only edit on existing keys (no new keys, no schema change)
- Test-only addition

**Scope rules:**
- Stay strictly inside the files listed in the Tasks above.
- Soft cap: ≤ 5 files, ≤ 50 non-test LOC changed (test-only additions are exempt from the LOC cap).

**Block-on-scope-expansion:** If implementing any task would require touching a file not listed above, adding a new branch / predicate / public API, changing a schema / key shape, or making a behavioral change in untested production code - **STOP and write `dev-state.json` with `status: blocked`**. Do not push past the constraint. A human PR reviewer is the only review gate for tiny; the diff must stay within these limits.
```

---

## Authoring Guidance

- **Keep it short.** Simple plans should fit on one screen. If you find yourself adding parallel groups, more than ~6 tasks, or a long acceptance-criteria list, the triage verdict was probably wrong - escalate to complex.
- **No groups.** Simple plans run as a single dev task. Do not introduce `group:` tags.
- **Affected Files feeds the Tasks.** `spec.md`'s `## Affected Files` is the starting file list - surface its contents in each task's `File:` line. `plan.md` has no standalone `## Affected Files` section.
- **Skip Acceptance Criteria** if the requirement is already concrete (one or two sentences describing exactly what to change). Add them only when the requirement leaves room for interpretation.
