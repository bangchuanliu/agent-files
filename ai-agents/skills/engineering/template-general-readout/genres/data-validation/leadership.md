# [System or Change] - Leadership Readout

**From:** [@owner] · **Date:** [date] · **Status:** [match the technical readout exactly]
**Full detail:** [link to technical readout]

An **extract**, not a summary of everything. Decision-relevant sections are lifted from the technical
readout; the rest is skipped and linked in the appendix. **Derive it - never author it
first.**

## Extraction map

| Tech section | Leadership treatment |
|---|---|
| §1 Executive Summary | **Extract** → §1 The ask |
| §2 Success Criteria | **Skip - link.** Thresholds are how we judged, not what we found. *Exception:* if a gate **failed**, the failure surfaces in §4 |
| §3 Data / System | **Skip - link.** *Exception:* §3a's baseline verdict, if `unaudited` or `disputed`, surfaces in §6 - it limits confidence |
| §4 Methodology | **Skip - link.** Never surfaces |
| §5 Results + §5a estimands | **Extract** → §2 What changes for customers |
| §6 Discrepancies | **Extract, compressed** → §3 Where the gap comes from |
| §7 Deep dive | **Extract, consequences only** → §4 |
| §8 Risk / Limitations | **Extract** → §5 and §6 |
| §9 Decision & Next Steps | **Extract** → §1 and §7 |
| Appendix A / B | **Skip - link** |

Skipping is not hiding: every skipped section is linked in the appendix, and any skipped
content that **limits the decision** is promoted into the body per the exceptions above.

---

## 1 · The ask

**Decision:** [the business decision, one sentence - in the terms the business uses].

- **Recommendation:** [SHIP / HOLD / ROLL BACK / PARTIAL / RAMP].
- **Owner / by when:** [@name] / [date].
- **Confidence:** [High / Medium / Low] - [the limiter, in plain words].

> If the decision is already made, this is a **decision record**. Retitle to "The decision",
> state it as settled, and convert §4 from blockers into commitments. A document that argues
> the opposite case from the decision it records reads as unresolved.

| Decision needed | Who decides | By when |
|---|---|---|
| `[Function]` [a genuine business decision, not an engineering task] | | |

---

## 2 · What changes for customers

**[Customers] would see [X%] [fewer / more] [units] than today.** [What it looks like to
them; whether billing is affected.]

**State any condition the headline depends on here - not in the caveats.** If the number
holds only when an unverified assumption is true, and the alternative is materially
different, that belongs beside the number.

| | Today | After | Difference |
|---|---|---|---|
| What customers see | | | **[X%]** |
| - of which intentional | | | |
| - of which genuine shortfall | | | |
| [Customers affected] | | | |

If the baseline is a corrected figure rather than one lifted from a single system, **show the
correction steps** - a derived headline that cannot be found in the source reads as invented.

**Intended differences still count as customer impact.** Say the change is deliberate, and
still count it - the customer experiences it either way.

**For context:** [prior period / comparable product / industry norm]. **If no benchmark
exists, say so explicitly** - the reader cannot otherwise judge whether the number is large,
and its absence is itself decision-relevant.

---

## 3 · Where the gap comes from

Three to five plain-language lines. Consequence, not mechanism. Each carries its share.

- **[Cause in plain words]** - [share], [explained / still unexplained].

Keep the **unexplained** portion visible. It is the reason confidence is not High.

---

## 4 · Why we are not ready yet - *or* What gates the cutover

Pick one framing and hold it:

- **HOLD** → "Why we are not ready yet." Blockers, each with cost, owner, date.
- **SHIP or RAMP** → "What gates the cutover." Split into what must be done *before exposure*
  versus what proceeds *in parallel*. Do not present solved problems as blockers.

Each bullet: problem in plain words · cost in customer or money terms · owner · date.

- **[Problem].** [Cost.] *[@owner], [date].*

**Include the risk in the other direction** if one exists - over-reporting reaches invoices
and is usually the more expensive direction. A positive discrepancy is never "no impact."

**If a §2 success criterion failed, it appears here** as a consequence - not as a threshold
table.

---

## 5 · Risk and timing

| | |
|---|---|
| If we ship now | [consequence in customer/billing terms] |
| If we hold | [cost of delay. **Holding is not zero-risk** - state what continuing on the current system exposes us to] |
| Earliest readiness | [date] - assumes [binding dependency] |
| How we back out | [mechanism, measured time to revert, or "undefined"] |

---

## 6 · What this does not tell you

Mandatory. Material and quantified.

- **[Whether either side is established as correct]** - if neither is, say so plainly; "X%
  fewer" may equally mean the current system is X% too high. **If the baseline verdict in
  tech §3a is `unaudited` or `disputed`, it belongs here.**
- [The figure that must not be quoted as revenue or as final, and why.]
- [Any headline condition still unverified, and what the number becomes if it fails.]
- [Anything still being reconciled - magnitude, and whether it could move the headline.]
- [Any prior finding now retracted, and what not to act on until it is settled.]

---

## 7 · Next steps

| # | Action | Owner | By when |
|---|---|---|---|
| 1 | | | |

---

## Appendix - Where the detail lives

Skipped sections, linked. Anyone asking "how do you know?" goes here.

| Question | Section | Link |
|---|---|---|
| How did we judge pass vs fail? | Tech §2 - Success criteria and thresholds | [link] |
| What exactly was compared, and against what? | Tech §3 - Data / system under validation | [link] |
| Is the reference trustworthy? | Tech §3a - Baseline audit | [link] |
| How was the validation performed? | Tech §4 - Methodology | [link] |
| Full results with thresholds | Tech §5 - Results | [link] |
| Every discrepancy and its cause | Tech §6, §7 | [link] |
| Underlying data and queries | Tech Appendix A - Evidence index | [link] |
| Publication checks | Tech Appendix B - Publication checks | [link] |

Deep links to headings where the platform supports them; the section number alone is not a
link. **Every row resolves, or the row is removed** - a dead pointer is worse than no
appendix.

---

## Derivation rules

**No new numbers.** Every figure traces to the technical readout. If one is missing, add it
there first, then re-derive. Values, rounding, units, recommendation and draft status match
exactly - a divergence is a defect. Regenerate rather than patch.

**Simplify language, never the conclusion.** Softening a caveat, promoting "fix scoped" to
"fix known", or dropping a named limitation is a fidelity failure even when every number is
right.

**Skip ≠ omit.** A skipped section is linked. A skipped section that limits the decision is
promoted into the body - see the extraction-map exceptions.

| Strip | Never strip |
|---|---|
| Reason codes, table and dataset names, filters, per-entity IDs, method mechanics, tie-outs, evidence index, run provenance, threshold parity detail | Customer-visible number, both estimands where they differ materially, recommendation, owner and date, confidence and its limiter, direction-risk item, cost of delay, reference point, limits section |

**Cross-references must resolve.** If the body promises a follow-up item, the item exists.
