# [System/Change] - Validation Readout

**Authors:** [@owner] · **Date:** [date] · **Status:** [from the publication checks - Appendix B]
**Leadership version:** [link, if any] · **One-pager:** [link, if any] · **Evidence:** [link]

---

## 1. Executive Summary

**Objective.** [What was being validated, as one sentence.]

**Scope.** [Dataset · pipeline · population · time window (N days inclusive, clipping noted) ·
environment.]

**Key findings.** Two to four bullets. Each carries a number and its basis.

- [Finding with figure.]
- [Finding with figure.]
- [The risk in the *other* direction, if one exists - a positive discrepancy is a finding.]

**Decision / recommendation.** [VALIDATED / VALIDATED WITH CAVEATS / NOT VALIDATED] →
[SHIP / HOLD / ROLL BACK / PARTIAL / RAMP]. Confidence [level], limited by [what].

> Validation status and rollout decision are **two different statements**. A pipeline can be
> validated and still not ship (org not ready, no rollback); it can ship unvalidated behind a
> ramp. State both, and never let one imply the other.

**Major risks / follow-ups.** [Anything preventing full confidence, quantified.]

**Two estimands - do not collapse into one number.**

| | Δ | Use it for |
|---|---:|---|
| **Customer-visible impact** - includes intended differences; removes only demonstrated errors | | what the customer or biller experiences |
| **Normalized residual** - further removes intended differences | | the size of the engineering defect |

---

## 2. Validation Objective & Success Criteria

Declare thresholds **before** running the comparison. A threshold authored after the results
are seen is not a criterion - mark it `post-hoc` and it cannot produce a Pass.

| Area | Validation question | Success criteria | Pre-registered? |
|---|---|---|---|
| Completeness | Are all expected records present? | ≥[99.9%] | Y/N |
| Accuracy | Do outputs match the reference? | ≥[99%] | Y/N |
| Consistency | Are aggregates consistent across systems? | <[1%] variance | Y/N |
| Timeliness | Are events processed within SLA? | ≥[99%] within SLA | Y/N |
| Schema | Are fields/types/nullability correct? | [100%] | Y/N |
| Edge cases | Are special cases handled correctly? | [100%] expected cases | Y/N |

**Basis of the criteria.** [Why these numbers - error model, business tolerance, prior
cutover, or "chosen by judgement" if so. A threshold with no basis is a guess with a decimal
point.]

---

## 3. Data / System Under Validation

- **Source.** [Where the data comes from.]
- **Transformation.** [What processing happens.]
- **Output.** [Exactly what is being validated - metric, grain, dedup policy, sign convention.]
- **Reference / baseline.** [What is being compared against - **and see the audit below**.]
- **Time window.** [start → end]; clipping applied identically to both sides: [detail].
- **Traffic / population.** [Volume · sampling · inclusion rule · matched / baseline-only /
  new-only counts · zero-denominator handling · blank vs 0.]
- **Environment.** [production / staging / offline replay.]

```
Source Events
     ↓
Data Collection
     ↓
Processing / Transformation
     ↓
Validated Output
     ↓
Reporting / Serving
```

Mark on the diagram the stage each compared table is drawn from. **Two tables at different
stages are not a like-for-like comparison** - a stage mismatch presents as a volume delta and
is the most common false finding in migration work.

### 3a. Baseline audit - the reference is not ground truth until audited

A second count establishes a **discrepancy, not correctness**. Do not fill "Reference =
ground truth" without completing this.

| Source | Count |
|---|---|
| [new system] · [alternative baseline] · [baseline used] | |

**Comparability:** metric semantics [ ] · grain [ ] · population [ ] · eligibility [ ] ·
identity coverage [ ] · window [ ] · filters [ ] · maturity [ ] · **pipeline stage** [ ].
Residual non-equivalence and its size: [ ].

**Verdict: [audited / unaudited / disputed].** [Demonstrated error and its scope. If the
result covers a wider scope than the evidence, state the extrapolation and bound it.]

**If the reference cannot be reconciled row-level** (no shared key), say so - the difference
is then *characterised*, not *proven*, and every downstream conclusion inherits that limit.

---

## 4. Validation Methodology

How the validation was performed. Omit categories that do not apply; do not omit ones that do
and leave the reader to assume they passed.

**A. Record-level** - ID matching · missing records · duplicate records · field-level
comparison.

**B. Aggregate-level** - record counts · success counts · value totals · outcome counts ·
match rate · breakdown by dimension.

**C. Distribution** - compare across region · platform · customer segment · account type · event type ·
processing window · [other]. A matching total with a diverging distribution is a failure, not
a pass.

**D. Edge cases** - nulls · late events · duplicates · out-of-order events · invalid
timestamps · boundary conditions · empty datasets · extreme values.

**Threshold parity.** [Every filter, gate or confidence cut applied in the analysis but not in
production, or vice versa. A mismatch means the measured delta is not the shippable delta.]

**Input transformations.** One row per normalise / hash / join / tokenise step between raw
source and compared rows. Silent input corruption is invisible in a result diff.

| Step | Affected scope | Quantified residual error | Material? |
|---|---|---|---|
| | | | |

---

## 5. Results

Absolute numbers **and** delta **and** the acceptance threshold. "The results look good" is
not a result; "event counts differ by 0.015%, against a 0.1% threshold" is.

| Metric | Reference | New pipeline | Delta | Threshold | Status |
|---|---:|---:|---:|---:|---|
| Events | | | | <[0.1%] | Pass/Fail |
| Successful outcomes | | | | <[0.5%] | |
| Value total | | | | <[0.5%] | |
| Derived outcomes | | | | <[1%] | |
| Match rate | | | | <[1pp] | |
| **TOTAL** | | | **[headline %]** | | |

**Reference point.** [Prior period / peer signal / equivalent legacy metric - without one, the
reader cannot judge whether the delta is large. If none exists, say so; that is itself
decision-relevant.]

**Sensitivity.** [Headline excluding each major component.]

### 5a. Two estimands, reported separately

| Estimand | Reference basis | New basis | Gap | % |
|---|---|---|---|---|
| As measured | | | | |
| **Customer-visible impact** (less demonstrated errors only) | | | | |
| **Normalized residual** (further less intended differences) | | | | |

**Every percentage names its denominator.** Deltas on different bases are not additive and
must not be compared without their basis stated.

**Tie-out:** computed [n] · stated [n] · discrepancy [n] · tolerance [exact for integer
counts] · unexplained remainder [n].

---

## 6. Breakdown of Discrepancies

Often more important than the headline match rate. Every row sums into §5.

| Discrepancy | Impact | Root cause | Class | Action |
|---|---:|---|---|---|
| [Late events] | [0.08%] | [Different processing cutoff] | Demonstrated error / Intended difference / Sensitivity / **Unexplained** | [Align watermark] |
| | | | | |
| **Total** | **[x%]** | | | |

`Unexplained` is a legitimate and required class. A discrepancy with a plausible story but no
evidence is **Unexplained**, not explained - record the story in §7 as a hypothesis.

**Direction matters.** State which directions are billing- or safety-relevant in this domain.
Until correctness is established, write *positive / negative discrepancy*, not over-count /
under-count, and name the check that would settle it. Never record a positive discrepancy as
"no impact."

---

## 7. Deep Dive / Root Cause

For every material discrepancy, in this order:

**Symptom → Investigation → Root Cause → Impact → Resolution**

> **Symptom.** Outcome count was 0.3% lower in the new pipeline.
> **Investigation.** Difference isolated to records arriving >24h after the source event.
> **Root cause.** New pipeline applies a 24h watermark; reference allows 48h.
> **Impact.** <0.1% on reported outcomes after the 7-day reconciliation period.
> **Resolution.** Extend watermark to 48h. *[@owner], [date].*
> **Status.** ✅ established / ⚠️ hypothesis - [the check that would settle it].

One primary cause per entity (`Unknown` allowed), plus secondary causes, signed
contributions, and the remainder *within* labelled entities. **Label coverage is not explained
impact** - report coverage by entity count, absolute movement and exposure, and always state
the cohort selection rule including any spend/volume/rank gate.

Detailed per-entity and per-cause tables stay in the evidence layer.

---

## 8. Risk / Limitations

State explicitly what was **not** validated. Material and quantified - not a caveat inventory.

- **Scope not covered.** [Only US traffic · only 5% of production · Android excluded ·
  downstream optimization not validated · 7-day window not included.]
- **Correctness vs agreement.** [Neither side established as correct, if so. Keep
  *demonstrated* and *suspected* apart.]
- **Uncertainty by evidence type.** Experiment → randomisation unit, interval, practical
  threshold, guardrails. Historical census → no sampling interval; state coverage, maturity,
  stability, sensitivity to definitions. Observational → association, not causation.
- **Figures that must not be quoted** as revenue, or as final.
- **Still being reconciled**, with magnitude - and whether it could move the headline.
- **Performance/latency** not covered by a correctness validation, if so.

---

## 9. Decision & Next Steps

**Validation status: [PASS / PASS WITH CAVEATS / FAIL]**
**Rollout decision: [SHIP / HOLD / ROLL BACK / PARTIAL / RAMP]**
Confidence [level] - limited by [what]. [Two or three sentences tying it to §5a and §7,
including the honest positive.]

**Validated:** [ingestion · dedup · business logic · aggregate reporting].
**Known limitations:** [late-arriving events · non-US traffic].

| # | Gate | Measurable pass condition | Current | Owner | Due | Pre-registered? | Blocks rollout? |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | Y/N | **Yes** |

An unknown owner or date is a gate **FAIL**, not a blank cell.

**Next steps.**

| # | Action | Owner / due | Pri | Expected recoverable effect + **benchmark anchoring it** | Verification |
|---|---|---|---|---|---|
| 1 | | | P0/P1/P2 | [an observed gap is not automatically recoverable] | |

**Alternatives considered:** do-nothing · partial rollout · shadow-run · [other] - and why
this beats each. Presenting a single option invites the reader to invent a worse one.

**Rollback / ramp:** [mechanism · trigger · measured time to revert, or "undefined" if so].
Reverting *reporting*, containing *billing* and repairing *already-issued* outputs are three
different mechanisms.

**Decision record:** analyst recommendation [ ] · data-owner position [ ] · escalation owner
[ ] · approver [ ] · outcome and date [pending - *a decision owner is not a decision*].

---

## Appendix A - Evidence index and provenance

**Evidence index:** [section → stable reference, both directions].
**Provenance:** [run ID / data-as-of · query or notebook revision · frozen snapshot · taxonomy
version · prior readout and what changed · cluster, catalogs, partition ranges per leg · each
figure classified measured / estimated / extrapolated / target].

## Appendix B - Publication checks

Author-side control; not part of the reader's document. The header Status field is this
result. A calling domain skill may supply its own checklist here. With no domain checklist,
record at minimum: evidence provenance · arithmetic ties · both estimands present · owner and
date set. Missing evidence is
**UNVERIFIED, never PASS**; any FAIL or material UNVERIFIED ⇒ **Draft**.

| # | Check | Result | Evidence / remediation |
|---|---|---|---|
| 1 | | | |
