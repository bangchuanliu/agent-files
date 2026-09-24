# Data Investigation Doc - Standard Structure

Use this structure whenever producing a **data investigation / discrepancy / RCA write-up**
(count mismatch, parity gap, pipeline anomaly, oncall data incident).
Not for code files, design docs, or runbooks.

## Core principles

1. **Answer first.** TLDR is section 1, not section 2. Most readers stop there.
2. **Quantify everything.** "Conversions dropped" → "‑12.4% (1.82M → 1.59M), 2026‑08‑01..08‑14".
3. **Every claim carries reproducible evidence** - the exact query + the result it produced.
4. **Separate fact from hypothesis.** Label confirmed / likely / ruled out.
5. **Record what you did NOT check** so the next reader knows the blind spots.
6. **Fully-qualified table names + partition/date range**, always. Never a bare table alias.

## Section skeleton

```markdown
# <Short title: system + symptom + date range>

| | |
|---|---|
| Author / Date | banliu / YYYY-MM-DD |
| Status | Draft \| Under review \| Confirmed \| Closed |
| Severity / Impact | e.g. P2 - 12% conversion undercount, 14 days |
| Links | JIRA, PR, Slack thread, dashboard, upstream doc |

## 1. TLDR
- **Symptom:** <one line, quantified>
- **Root cause:** <one line, mechanism + origin (PR/config/upstream change)>
- **Impact:** <rows / % / date range / downstream consumers>
- **Fix & status:** <mitigation, backfill, owner, ETA>
- **Confidence:** High / Medium / Low + why

## 2. Context & Background
What pipeline/flow, what is expected-correct behavior, what triggered this
investigation (alert, user report, launch), and what changed recently.

## 3. Scope & Method
- Tables & partitions queried (FQN + date range)
- Tools (Trino/Spark or notebook/query environment), environment (production vs development)
- Assumptions
- **Out of scope / not checked**

## 4. Evidence
One numbered subsection per finding. Each: Claim → Query → Result → Interpretation.

### 4.1 <Finding>
**Claim:** ...
**Query:** (link to appendix or inline, with partition filters)
**Result:** (small table; put the big one in the appendix)
**Interpretation:** what this does and does not prove.

### 4.x Hypotheses ruled out
| Hypothesis | How tested | Verdict |

## 5. Root Cause
Symptom → mechanism → origin (commit / config / upstream schema change),
plus **magnitude check**: does this cause fully explain the observed delta?
Note any residual unexplained portion.

## 6. Impact & Blast Radius
Affected rows/%, date range, downstream tables, dashboards, reporting/revenue/
compliance exposure, whether data is recoverable.

## 7. Remediation
| Action | Type (mitigate/fix/backfill) | Owner | Status | Verification query |

## 8. Prevention & Monitoring
Alerts or DQ checks that should have caught this; the gap; what to add.

## 9. Open Questions / Next Steps
Owner + date for each.

## Appendix
- A. Tables: FQN, partition scheme, owner, source repo/job
- B. Full queries (copy-pasteable)
- C. Full result sets / screenshots
- D. Glossary & changelog of this doc
```

## Anti-patterns

- Burying the conclusion after 3 pages of queries.
- Evidence without the query, or query without the partition filter.
- "Looks like" / "seems to" without a confidence label.
- Correlation presented as root cause without a magnitude check.
- Table names without database prefix or date range.
