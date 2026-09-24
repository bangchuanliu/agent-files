---
name: generate-plan
kind: leaf
description: "Generate an execution plan (plan.md) for a triaged feature from its spec.md. Use when: write plan, execution plan, decompose feature, parallel groups, tech lead plan."
---

# generate-plan - Execution Plan Generator

Produce an implementation plan for a feature whose `spec.md` already contains a triaged `## Requirement` and `## Triage`. Picks the matching template (simple or complex), decomposes the work, and writes a **separate** `plan.md`. `spec.md` is read-only - never edited, and `plan.md` does NOT duplicate Requirement/Triage.

**Inputs from the calling agent:**
- `feature_name`
- `skip_review` (default `false`) - when `true`, skip the Step 6 review and write `plan.md` directly. Used when the caller (e.g., an orchestrating pipeline skill supplied by a company layer) owns user-facing review at a higher level.
- `revision_feedback` (optional) - free-text feedback from a prior rejection. Incorporate into Steps 3–4 before re-writing.
- Targeted-read codebase context (repo-specific style/architecture references + affected-file notes)

**Output:** `plans/features/<feature_name>/plan.md` - routing frontmatter copied from `spec.md`, body per template.

---

## Step 1: Validate Inputs

Read `plans/features/<feature_name>/spec.md`.

Required:
- YAML frontmatter with `complexity: simple | complex | tiny` AND `needs_qa: true | false`
- `## Requirement` section
- `## Triage` section (verdict + dimension table)

If any is missing, **stop and report**:

```
spec.md missing required sections (Requirement / Triage / complexity).
complexity must be simple | complex | tiny.
Run the triage/orchestration skill for this repo first to produce a triaged spec.md.
```

Then check whether `plans/features/<feature_name>/plan.md` already exists with a `created:` field in its frontmatter. If so, the plan was previously TL-enriched - do NOT re-run unless `revision_feedback` is explicitly passed; stop and report that the plan is already enriched. (`created:` is the universal "tl-enriched" marker for both simple and complex plans.)

## Step 2: Load Template

| Frontmatter `complexity` | Template |
|---|---|
| `simple` | `simple-plan.md` |
| `complex` | `complex-plan.md` |
| `tiny` | `simple-plan.md` (linear tasks, no groups) |

Read the matching file from `.claude/skills/generate-plan/<template>` (relative to repo root, falling back to `~/.claude/skills/generate-plan/<template>`).

The template defines the section structure and frontmatter fields the final `plan.md` must contain.

For `tiny`, every task must be a drop-in, allow-listed edit (doc/comment, log message, constant tweak, rename, dead-code removal, YAML value-only edit, test-only addition).

## Step 3: Decompose Work

Using `spec.md`'s `## Requirement`, `## Triage`, `## Affected Files`, and the targeted-read context:

1. **Map every acceptance criterion** to one or more tasks. Do not invent criteria; do not drop any.
2. **For each task, name the file(s) it touches** and the action (`create | modify | delete`). Use `spec.md`'s `## Affected Files` as the starting list; open a listed file if its details are thin. Do NOT launch broad discovery beyond the spec's file list.
3. **Order tasks by dependency** within their group. Earlier tasks must not depend on later ones.
4. **List risks** - anything that could block completion or surprise reviewers (data migrations, config schema changes, downstream consumers, performance hot paths).
5. **If `revision_feedback` was passed**, treat it as the highest-priority signal: re-decompose to address the concerns. Note in the plan's risks/notes how each point was incorporated (or rejected, with reasoning).

## Step 4: Assign Parallel Groups (complex only)

Skip for simple/tiny - single linear task list.

For complex plans:
- Group tasks for concurrent execution by up to **3 dev agents** (`A`, `B`, `C`).
- **Different groups MUST touch completely distinct files.** Two tasks touching the same file share a group.
- Aim for 2–3 roughly equal groups by task count and risk.
- Same-group tasks execute sequentially by one agent.

The calling agent may supply repo-specific group patterns (e.g., Config YAML / Core Scala / Tests + Airflow). Use them as a starting point but adapt to the actual file set.

## Step 5: Determine Branch Name

Run `git branch --show-current`.

- **On `master` or `main`**: branch name = `<ldap>/<feature_name>` (resolve LDAP via `whoami`). The calling pipeline usually creates the branch before this skill runs - if already on a feature branch, use the current branch.
- **On any other branch**: branch name = current branch.

This value goes into the frontmatter `branch:` field. Do not switch branches from inside this skill.

## Step 6: Present Plan for Review (caller-controlled)

**Skip when ANY of the following is true:**
1. Caller passed `skip_review: true` (e.g., an orchestrating pipeline skill owns review at the manager level).
2. Frontmatter already has `created:` (re-enrichment pass).

**Otherwise** (standalone invocation), present the full draft via `AskUserQuestion` **before writing to disk**:

```
## Plan: <feature_name>

Ticket: <ticket from spec.md, or "none">
Branch: <branch_name>
Created: YYYY-MM-DD

<rendered template body>

---

Approve? Type "yes" to proceed, or describe what to change.
```

If rejected: read the feedback, revise (loop back to Step 3 or Step 4), and re-present until approved. **Do not write `plan.md` without approval** in this mode.

**`skip_review: true` mode:** write `plan.md` directly (Step 7). The caller reads it and appends `approved: <date>` on approval, or re-invokes with `revision_feedback` on rejection.

## Step 7: Write the Plan

Write a **fresh** `plans/features/<feature_name>/plan.md` (separate from `spec.md`). Do NOT edit `spec.md`.

1. **Frontmatter** - copy routing fields from `spec.md` (`feature_name`, `complexity`, `needs_qa`, `route`, `ticket`), then add:
   - `branch: <branch_name>` (Step 5)
   - `created: YYYY-MM-DD`
   - Complex only: `phases:` (list of group summaries)
2. **Body** - rendered template body only. Do **NOT** copy `## Requirement` or `## Triage` into `plan.md`; those stay in `spec.md`. `spec.md`'s `## Affected Files` informs each task's `File:` line.

Final structure:

```markdown
---
<routing fields copied from spec.md + added TL fields>
---

# <feature_name>

<rendered template body - Summary, Acceptance Criteria, Tasks, Risks>
```

**Completeness check before writing:**
- Every acceptance criterion maps to ≥ 1 task.
- Every task has `file` + `action` + `details`.
- (Complex) No file appears in more than one group.
- (Complex) Tasks within a group are ordered by dependency.
- **(Tiny) The `## Constraints` section is present.** A tiny plan without it is invalid - the Constraints section is the only scope guard for the implementing agent. If missing, add it before writing.

If any check fails, fix and re-present (Step 6).

**For `complexity: tiny` - mandatory `## Constraints` section:**

Append the following verbatim (adapt wording, keep all substance) after `## Risks`:

```markdown
## Constraints

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

For `simple` or `complex`, omit `## Constraints`.

## Step 8: Return

Return to the calling agent:
- Path to `plan.md`.
- Number of tasks (and groups, for complex).
- Branch name.

Ticket is resolved by **triage** (the `ticket:` field is copied from `spec.md`); the user-facing summary is the caller's responsibility.

---

## Rules

1. **`spec.md` is read-only.** Never edit it. `## Requirement` and `## Triage` stay there; do not copy them into `plan.md`.
2. **Copy routing fields from `spec.md`** (`feature_name`, `complexity`, `needs_qa`, `route`, `ticket`) into `plan.md` frontmatter, then add the TL fields (`branch`, `created`, `phases` for complex). `ticket` comes from `spec.md` (triage owns it) - never derive it from the requirement.
3. **Plan review is caller-controlled.** `skip_review: true` → write directly, no `AskUserQuestion`. Omitted/false → run the in-skill review loop.
4. **Do not fabricate requirements.** If the requirement is ambiguous, surface it in risks/notes - do not guess.
5. **No file in two groups.** Same-file tasks share a group.
6. **One section per concern.** Tasks under `## Tasks`; risks under `## Risks`. No scattered TODOs.
