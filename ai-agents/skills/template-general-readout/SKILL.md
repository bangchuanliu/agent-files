---
name: template-general-readout
kind: leaf
description: "Readout skeleton: choose sections for strategy, launch, research, program, incident, or data-validation readouts. Branches: pick genre; emit skeleton; adapt for leadership. Prefer specialized validation or RCA skills when they exist. NOT for: RCA narrative -> use template-doc-data-issue-rc; running checks -> use validation skills."
---

# General Readout Template

A readout is a document that ends in a **decision or an ask**, backed by evidence. This skill
holds the skeletons only - pick the genre, take the sections, fill them from your own
material. It deliberately carries no methodology; the specialised skills do that.

## Pick the genre

| Genre | The question it answers | Go deeper in |
|---|---|---|
| **Data validation / migration** | Do the new numbers match, and can we ship them? | If the environment supplies a data-validation readout skill, prefer it; otherwise use the generic skeleton below |
| **Strategy / exploration** | Is this area healthy, and what should we start, stop or continue? | - |
| **Launch / staged rollout / GA** | Did this stage meet its criteria, and do we advance? | - |
| **Qualitative research** | What did customers tell us, and is the concept validated? | - |
| **Program / portfolio review** | Across N workstreams, where do we invest? | - |
| **Incident / postmortem** | What broke, what did it cost, what prevents recurrence? | `template-doc-data-issue-rc` for data RCAs |

If two genres fit, pick by the **ask**, not the content.

## Universal spine

Every genre carries these. Order may vary; presence may not.

1. **Header** - author, date, status (draft/final), scope and period, link to evidence.
2. **TL;DR** - the answer and the ask, written last, placed first.
3. **The ask** - decision, owner, date, recommendation, confidence and what limits it.
4. **Evidence and method** - what you looked at, how, and the population or sample.
5. **Findings** - only those that can change the decision. Each with a ✅ established /
   ⚠️ not yet proven verdict.
6. **Recommendation** - with alternatives considered.
7. **Next steps** - work, owner, priority, effort, timeline.
8. **What this does not tell you** - the limits of the claim. Never optional.
9. **Appendix** - detail, references, glossary if the audience needs it.

## Genre skeletons

Sections *in addition to* the universal spine.

### Strategy / exploration
- Problem framing - why this was explored
- Tenets - the principles the recommendations follow, stated before them
- Findings tagged by the outcome they affect (acquisition / efficacy / retention / friction)
- **Start / Pause / Continue** - the recommendation shape for a portfolio of bets
- Workstreams - work · impact · priority · level of effort
- Impact estimation - projected effect **plus the benchmark it is anchored on**

### Data validation / migration
- Decision frame - ship / hold / rollback / continue ramp, with owner and date
- Systems compared - new source, baseline source, grain, metric definitions, date range
- Parity summary - expected tolerance, actual delta, pass/fail by critical metric
- Impact summary - who or what changes, magnitude, materiality threshold, top movers
- Root-cause summary - known causes, residual unexplained delta, confidence
- Readiness checklist - validation complete, monitoring ready, backfill or correction plan, consumer communication
- Recommendation - decision, alternatives considered, and rollback trigger

### Launch / staged rollout / GA readiness
- Rollout overview - type, stage history, cohort, exposure mechanism, reach
- **Pre-determined graduation criteria** - agreed before the stage, must-have vs nice-to-have
- Stage-by-stage results - participation, feedback themes, issues by severity
- Results vs criteria - target · actual · met?
- GTM readiness checklist - docs, pricing, enablement, support, comms, legal, monitoring
- Risks - likelihood · impact · mitigation
- Rollback plan - trigger, mechanism, time to revert

### Qualitative research
- Objective, participants and composition, method, interview/discussion guide
- Findings with verbatim quotes attributed to a role
- **"The so what"** per section - ✅ validated / ⚠️ needs proving
- **Sample-bias disclosure** - how this cohort differs from the population
- Self-reported numbers labelled as stated preference, never as forecast
- Appendix - participant table, transcripts or a searchable transcript index/tool

### Program / portfolio review
- Workstream inventory with status and owner
- Cross-workstream themes and dependencies
- Investment recommendation per workstream - invest / hold / stop
- Aggregate risk and resourcing picture

### Incident / postmortem
- Impact - who, how many, how long, what it cost
- Timeline - detection, escalation, mitigation, resolution
- Root cause, with the evidence that pins it
- Contributing factors and what made it hard to detect
- Prevention and detection actions with owners

## Audience

Produce a technical version for the owning team, and derive a one-page leadership version
when the decision leaves the team. **Derive, never author leadership first**: no new numbers,
values and status must match, simplify language but never the conclusion.

## Craft rules

- Write the TL;DR last; lead with the answer, not the journey.
- Every number has a source; every estimate names its benchmark.
- Say whether a number is good, not only what it is - anchor to a prior period or peer.
- Keep *demonstrated* and *suspected* apart, in every section.
- Include a section only if it changes the decision. Empty scaffolding is noise.
