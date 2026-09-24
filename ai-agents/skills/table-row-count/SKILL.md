---
name: table-row-count
kind: leaf
description: "Compare row counts between source and target tables. Use when: row count, count comparison, row diff. NOT for: row-level diffs or key integrity (table-traceability-check), null rates (table-null-check), duplicate keys (table-duplicate-check), schema drift (table-schema-check), freshness (table-freshness-check), distribution drift (table-distribution-check), or source-to-target traceability (table-traceability-check) - counts only."
---

# Data Row Count - Source vs Target Comparison

Compare total row counts between source and target tables for the same logical day.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Source table name (Trino path)
- Target table name (Trino path)
- Partition date (`YYYY-MM-DD` or `YYYY-MM-DD-HH`)
- Filters (optional)
- Match mode: `exact` or `ratio`

## Modes

- **Exact match** (1:1 source-target comparisons): `diff_pct` should be 0% or near-zero.
- **Ratio match** (filtered or transformed target comparisons): target applies additional filters. Track target/source ratio against a baseline.

## Query

```
diff_pct = ABS(target_count - source_count) / GREATEST(target_count, source_count) * 100
```

## Thresholds

| Condition | Outcome |
|-----------|---------|
| diff_pct = 0 (exact) or within baseline (ratio) | PASS |
| diff_pct <= 0.01% | WARN |
| diff_pct > 0.01% | FAIL |


## Output

Return JSON:
```json
{
  "check": "row_count",
  "source_count": 0,
  "target_count": 0,
  "diff_pct": 0.0,
  "result": "PASS"
}
```
