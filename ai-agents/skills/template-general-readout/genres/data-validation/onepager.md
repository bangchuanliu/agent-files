# One-Pager Template

A **compressed technical readout** - same vocabulary as `technical.md`, one screen. This
is *not* the leadership readout: it keeps metric names, deltas and thresholds. For a
business-language version with jargon stripped, use `leadership.md`.

## Two ways this gets used

**1 · Standalone - the simple-validation case.** The whole deliverable. Use when all four
hold: every gate passed against pre-registered thresholds · baseline verdict is `audited` ·
no material unexplained discrepancy · the two estimands agree. Routine recurring parity
checks that keep passing are the intended case. Author directly; no backing doc needed.

**2 · Derived - the compression case.** A complex validation squeezed onto one screen for a
reader who needs the verdict fast: staff channels, review-meeting pre-reads, status updates,
a PR or ticket description. Requires a completed `technical.md`. **Never author it
first** - every figure is copied, never recomputed.

**Which one you are in is not a style choice.** Fail any of the four standalone conditions
and you are in case 2, regardless of how short the result looks. A one-pager may stand alone
exactly when it has nothing complicated to say; a FAIL, a disputed baseline, an unexplained
gap or diverging estimands each need somewhere to show the work, and that is never a single
screen.

Fixed-width block so it renders in chat and terminals.

---

```
DATA VALIDATION READOUT
────────────────────────────────────────

Objective
Validate <new pipeline/system> against <reference>
for <population/time window>.

Success Criteria          [pre-registered: Y/N]
• Accuracy:     <agreed threshold>
• Completeness: <agreed threshold>
• Latency:      <agreed threshold and units>
• Downstream impact: <agreed materiality threshold>

Key Results
Metric              Reference    New       Delta      Threshold
<metric with units> <measured>   <measured> <computed> <agreed>
<metric with units> <measured>   <measured> <computed> <agreed>

Validation: <PASS / PASS WITH CAVEATS / FAIL>
Baseline:   <audited / unaudited / disputed>

Two Estimands
  Customer-visible impact        -X.X%
  Normalized residual            -Y.Y%

Key Findings
• <measured finding, including population and window>
• <measured finding and confidence limiter>

Discrepancy Analysis
• <signed contribution and shared denominator> [demonstrated]
• <signed contribution and shared denominator> [intended]
• <signed remainder and shared denominator>    [unexplained]
• Total: <computed sum>

Risks / Limitations
• <coverage limitation, quantified>
• <pending check and its consequence>

Decision
Validation: <same status as above>
Rollout:    <SHIP / HOLD / ROLL BACK / PARTIAL / RAMP>
            <conditions and measurable gates>
Owner: <@name>   By: <date>

Next Steps
1. ...
2. ...
3. ...
```

---

## Rules

**Never strip these**, even for length - removing them changes the conclusion, not the detail:

- The **acceptance threshold** beside each delta. A delta without its threshold cannot be read
  as pass or fail.
- **Pre-registration status** on the criteria block. Thresholds authored after the results are
  seen cannot produce a `PASS`.
- **Baseline status** (`audited` / `unaudited` / `disputed`) next to Status. A `PASS` against
  an unaudited reference is an agreement measurement, not a correctness verdict.
- **Both estimands.** The single most common failure of a compressed readout is one number
  standing in for two different questions.
- **Validation status and rollout decision as separate lines.** They are different statements.
- The **unexplained** share in the discrepancy block, and its class labels.
- Owner and date. An unknown owner is a FAIL, not a blank.

**Sizing.** If it does not fit one screen, cut Next Steps to three and trim Key Findings -
never the threshold column, the estimands, or the limitations block.

**Discrepancy classes.** Tag each line `[demonstrated]`, `[intended]`, `[sensitivity]` or
`[unexplained]`, matching §6 of the technical readout exactly.

**Derivation check.** *(Case 2 only.)* Every number appears in the technical readout with
identical value, rounding and units. A divergence is a defect - regenerate, do not patch.

**Escalation.** If filling this in reveals a failed gate, an unaudited baseline, an
unexplained discrepancy or diverging estimands, **stop and write the technical readout.** The
one-pager is then derived from it. Discovering complexity mid-draft is the normal way case 1
turns out to be case 2 - it is not a reason to compress harder.
