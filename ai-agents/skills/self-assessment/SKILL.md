---
name: self-assessment
kind: leaf
description: Score and reframe a piece of work (PR description, design doc, journal note, weekly write-up, Slack thread) against the 11 career principles (3 leadership + 3 execution + 5 craftsmanship) and rewrite it to highlight quantified impact. Use when - self-assessment, self-review, reframe for impact, promo write-up, weekly review, daily journal review, "how do I describe this work", "rewrite this for impact", career self-evaluation.
---

# Self-Review Reframe

Score an artifact against the user's 11 career principles, then rewrite it to highlight quantified impact under each principle the work demonstrates.

Source of truth for the principles: `principles.md` (in this skill directory). Read it before scoring — it carries the "Impact looks like" hooks, BAD→GOOD patterns, "look for" signals, and anti-patterns the scoring and reframing depend on.

## The 11 Principles (L → E → C)

### Leadership (L) — the group's work

| Code | Principle | Look for |
|---|---|---|
| **L1** | Direction Setting | Drove design/architecture decisions for others, set standards, navigated ambiguity for the team |
| **L2** | Ownership Beyond Scope | Picked up unowned work, cross-project improvements, gap-finding without being asked |
| **L3** | Influencing Without Authority | Aligned stakeholders, built consensus, articulated trade-offs to unblock decisions |

### Execution (E) — your own work

| Code | Principle | Look for |
|---|---|---|
| **E1** | Technical Complexity & Problem Solving | Ambiguous/cross-system problem, why-it-was-hard, key design decisions |
| **E2** | Planning & Timeline Management | Milestones, sequencing, dependencies, scope/time trade-offs, plan adjustment |
| **E3** | Risk Identification & Mitigation | Risks named early, fallback, blast-radius reduction, incidents prevented |

### Craftsmanship (C) — engineering quality and leverage

| Code | Principle | Look for |
|---|---|---|
| **C1** | Elegant, Simple, Maintainable Code | High quality bar, clear structure, simplest abstraction that fits |
| **C2** | Reuse-First Mindset | Designed for multiple consumers, shared utility, generalization at the right level |
| **C3** | Craft Processes & Mature Testing/Monitoring | Test coverage of failure modes, alerts tied to user impact, runbooks, quality gates |
| **C4** | Reviewing Others' Work | Substantive review comments, design-phase issues caught, coaching feedback |
| **C5** | Metrics-Driven Improvement | Before/after numbers, dashboards exposing issues, data-backed decisions |

**Impact & Outcomes is the measure across L, E, and C.** Every reframed line must surface a quantified result: revenue, cost, latency, accuracy, reliability, adoption, risk reduction, downstream teams unblocked, decisions unblocked, reuse, MTTR. Use rough numbers if exact ones aren't available.

## Process

### 1. Read the artifact

Inputs the skill accepts:
- A file path (`.md`, `.html`, `.txt`, PR description file)
- Pasted text
- A PR URL (`gh pr view <num> --json title,body,commits`)
- A journal section

If multiple artifacts are given (e.g., a weekly review), score each separately, then aggregate gaps at the end.

### 2. Score each principle

For each of L1–L3, E1–E3, C1–C5 produce one row:

| Status | Meaning |
|---|---|
| ✓ | Clearly demonstrated — at least one concrete sentence supports it AND impact is named (quantified or category-named) |
| ⚠ | Partial — touched but vague, no impact surfaced, or only implied |
| ✗ | Missing — no evidence in the artifact |

Cite a one-line quote from the artifact as evidence for ✓ and ⚠. Quote verbatim (truncate with `…` if long).

### 3. Reframe for impact

For every ✓ and ⚠ row, produce a rewritten sentence using the BAD → GOOD patterns in `principles.md`. The reframed sentence MUST surface an "Impact looks like" outcome from the matching principle:

- **BAD**: implementation-only, no decision, no impact ("I built X")
- **GOOD**: decision/risk/leverage framing + quantified result tied to the principle's impact category

If the artifact has no numbers, insert `[quantify: <metric>]` placeholders the user must fill in. Do not invent numbers.

### 4. Flag gaps

For every ✗ row, write one line: *"To add this principle, your artifact would need: <one concrete prompt from the principle's 'Look for' list>."*

Note when the work is **strictly execution scope** (all L1/L2/L3 are ✗). Ask whether there's a leadership angle that was left out, or whether this is genuinely exec-only work (which is fine and worth saying explicitly).

### 5. Output

Write the report directly into the chat — no separate file unless the artifact is large (>3 sections) or the user asks for a saved file. If saving, write to `/tmp/self-review-<slug>-<date>.md`.

Output template:

```markdown
# Self-Review: <artifact title>

## Coverage

| Principle | Status | Evidence |
|---|---|---|
| L1 Direction Setting | ✓/⚠/✗ | "<quote>" |
| L2 Ownership Beyond Scope | ✓/⚠/✗ | "<quote>" |
| L3 Influencing Without Authority | ✓/⚠/✗ | "<quote>" |
| E1 Technical Complexity & Problem Solving | ✓/⚠/✗ | "<quote>" |
| E2 Planning & Timeline Management | ✓/⚠/✗ | "<quote>" |
| E3 Risk Identification & Mitigation | ✓/⚠/✗ | "<quote>" |
| C1 Elegant, Simple, Maintainable Code | ✓/⚠/✗ | "<quote>" |
| C2 Reuse-First Mindset | ✓/⚠/✗ | "<quote>" |
| C3 Craft Processes & Mature Testing/Monitoring | ✓/⚠/✗ | "<quote>" |
| C4 Reviewing Others' Work | ✓/⚠/✗ | "<quote>" |
| C5 Metrics-Driven Improvement | ✓/⚠/✗ | "<quote>" |

## Reframed (impact-first)

**L1 — Direction Setting**
> <rewritten sentence with quantified impact from L1's "Impact looks like" categories>

…(one block per ✓/⚠ row, L principles first, then E, then C)…

## Gaps — what to add next time

- **<Code> <Principle>**: <one-line concrete prompt>
- …

## Verdict

<One sentence: strong / partial / exec-only. If exec-only, ask: is there a leadership angle?>
```

## Rules

1. **Use the user's vocabulary verbatim.** Do not invent new principle names or compress the 6 into fewer abstractions.
2. **Quote evidence, don't paraphrase.** The ✓/⚠ rows must cite the artifact's actual words.
3. **Never invent numbers.** Use `[quantify: …]` placeholders. The user fills these in.
4. **Always surface impact.** Every reframed sentence must include an outcome from the principle's "Impact looks like" categories. A reframe without impact is a failed reframe.
5. **No filler.** No "great work" / "this is solid". The output is a rubric + rewrite, not feedback theater.
6. **Push back on missing principles.** If an artifact is all E and zero L, say so plainly: "This is strictly exec-scope. Was there a leadership angle?"
7. **Stay concrete.** The reframed sentences must be drop-in replacements the user can paste into a PR description, promo doc, or resume bullet.
8. **Match register.** PR descriptions stay technical; promo write-ups can be more outcome-driven; journal entries can be first-person. Mirror the artifact's register, only upgrade the impact framing.

## Modes (optional flags)

- `--exec-only`: score only E1–E3 (use for pure execution-scope artifacts where leadership and craftsmanship scoring would be noise)
- `--no-craft`: score only L and E, skip C (use for process/strategy artifacts with no code component — e.g., a design doc whose craftsmanship implications are downstream)
- `--craft-only`: score only C1–C5 (use for pure code/PR review where L and E scope is not the point)
- `--weekly <file>`: input is a list of artifacts (one per line/section); produce per-artifact tags then an aggregate table showing which principles got reps this week and which were starved

## Example

**Artifact:**
> Built the conversion backfill pipeline. Ran for 3 days. Restated revenue numbers.

**Output:**

| Principle | Status | Evidence |
|---|---|---|
| L1 Direction Setting | ✗ | — |
| L2 Ownership Beyond Scope | ✗ | — |
| L3 Influencing | ✗ | — |
| E1 Technical Complexity | ⚠ | "Built the conversion backfill pipeline" |
| E2 Planning | ⚠ | "Ran for 3 days" |
| E3 Risk Mitigation | ✗ | — |
| C1 Maintainable Code | ✗ | — |
| C2 Reuse | ✗ | — |
| C3 Testing/Monitoring | ✗ | — |
| C4 Reviewing Others | ✗ | — |
| C5 Metrics-Driven | ✗ | — |

**Reframed:**

E1 — *Designed an idempotent conversion backfill across [quantify: N partitions / M advertisers] under correctness and billing-consistency constraints; resolved late-event and double-counting risks before replay, restoring revenue accuracy for the affected window.*

E2 — *Sequenced the 3-day backfill into validation, replay, and reconciliation stages with go/no-go checkpoints between each, keeping reporting available throughout instead of going dark.*

**Gaps:**
- **L1 Direction Setting**: To add this, describe the decision you forced (e.g., source-of-truth for restated metrics) that aligned product, finance, and DS.
- **L2 Ownership Beyond Scope**: To add this, name a gap you picked up that wasn't in the original ticket.
- **L3 Influencing**: To add this, describe a trade-off you exposed (freshness vs. correctness, scope vs. timeline) that unblocked a stakeholder decision.
- **E3 Risk Mitigation**: To add this, name what could have broken (double-counting, identity drift, billing variance) and how you prevented it.
- **C2 Reuse**: To add this, name whether the backfill became a reusable framework for the next backfill or stayed a one-off script.
- **C3 Testing/Monitoring**: To add this, describe the validation queries and monitoring you added (or wired into the existing pipeline) as part of the backfill.

**Verdict:** Exec-only and under-quantified, with no craftsmanship surface. Strong candidate for promo language once you add the L1/L2 angles, the C2/C3 follow-through, and fill the `[quantify: …]` slots.
