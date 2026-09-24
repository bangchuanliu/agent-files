---
name: table-null-check
kind: leaf
description: "Compute null-rate per critical column in a table, optionally diffing against a baseline. Use when: null rate, null check, null %, missing values, column completeness, null shift. NOT for: row totals (table-row-count), duplicate keys (table-duplicate-check), schema drift (table-schema-check), freshness (table-freshness-check), distribution drift (table-distribution-check), or source-to-target traceability (table-traceability-check) - null-rate only."
---

# Data Null Check - Per-Column Null Rate

Compute null rate for one or more critical columns in a single table, or diff null rates between two tables (baseline vs target).

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Target table name (Trino path)
- Partition filter
- Column list (one or more; expressions allowed, e.g. `outcome.source`)
- Optional baseline table for diff mode

## Single-Table Query

```sql
SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN <col> IS NULL THEN 1 ELSE 0 END) AS null_count,
  ROUND(100.0 * SUM(CASE WHEN <col> IS NULL THEN 1 ELSE 0 END) / COUNT(*), 4) AS null_pct
FROM <target_table>
WHERE <partition_filter>;
```

Run once per column. For nested fields, dot-access the path (`outcome.source`, `touchpoint.metadata.adEngagement.campaignUrn`).

## Diff-Mode Query

Run the single-table query against both tables, then compute `null_pct_diff = test_null_pct - baseline_null_pct` (signed; positive = test has more nulls).

## Thresholds

| Condition | Outcome |
|---|---|
| null_pct = 0 on a declared non-nullable column | PASS |
| null_pct > 0 on a declared non-nullable column | FAIL |
| Diff mode: \|null_pct_diff\| ≤ 0.1pp | PASS |
| Diff mode: 0.1pp < \|null_pct_diff\| ≤ 1pp | WARN |
| Diff mode: \|null_pct_diff\| > 1pp | FAIL |
| Null rate flips from 0% → nonzero on a PK column | FAIL (critical) |

## Output

Return JSON, one entry per column:
```json
{
  "check": "null_rate",
  "results": [
    {"column": "<col>", "null_pct": 0.0, "result": "PASS"},
    {"column": "<col>", "baseline_null_pct": 0.0, "test_null_pct": 0.05, "diff_pp": 0.05, "result": "PASS"}
  ]
}
```
