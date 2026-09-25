---
name: table-row-count
kind: leaf
description: "Row count check: compare source and target table counts for the same slice. Use when: row count, count comparison, row diff, source target volume check. NOT for: key-level orphans and field mismatches (table-traceability-check), null rates (table-null-check), duplicate keys (table-duplicate-check), schema drift (table-schema-check), freshness (table-freshness-check), or value distribution drift (table-distribution-check)."
---

# Table Row Count Check

Compare source and target row counts for the same logical slice. Use this as a volume gate only; use `table-traceability-check` when keys or field values must match.

## Inputs

- Source table or subquery: `<source_table_or_subquery>`.
- Target table or subquery: `<target_table_or_subquery>`.
- Source and target partition filters. Use equivalent logical windows, even if column names differ.
- Optional extra filters applied to both sides or documented as intentional asymmetry.
- Match mode: `exact` for 1:1 movement, `ratio` when the target is intentionally filtered or transformed.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific thresholds from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The query below is ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

```sql
WITH source_counts AS (
  SELECT COUNT(*) AS row_count
  FROM <source_table_or_subquery>
  WHERE <source_partition_filter>
    AND <optional_source_filter>
),
target_counts AS (
  SELECT COUNT(*) AS row_count
  FROM <target_table_or_subquery>
  WHERE <target_partition_filter>
    AND <optional_target_filter>
)
SELECT
  s.row_count AS source_count,
  t.row_count AS target_count,
  t.row_count - s.row_count AS diff_rows,
  100.0 * ABS(t.row_count - s.row_count)
    / NULLIF(GREATEST(s.row_count, t.row_count), 0) AS diff_pct,
  CASE
    WHEN s.row_count = 0 AND t.row_count = 0 THEN 1.0
    ELSE 1.0 * t.row_count / NULLIF(s.row_count, 0)
  END AS target_source_ratio
FROM source_counts s
CROSS JOIN target_counts t;
```

For `ratio` mode, compare `target_source_ratio` with the accepted baseline ratio from local context or prior healthy partitions. Do not treat a ratio mismatch as a traceability failure unless key joins were checked separately.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| Exact mode: `source_count = target_count` | PASS |
| Exact mode: `diff_pct <= 0.01` | WARN |
| Exact mode: `diff_pct > 0.01` | FAIL |
| Ratio mode: ratio within configured baseline tolerance | PASS |
| Ratio mode: ratio outside tolerance but direction is explained by documented filters | WARN |
| Ratio mode: ratio outside tolerance and unexplained | FAIL |
| One side is zero and the other is nonzero | FAIL |

## Output format

Return JSON:

```json
{
  "check": "row_count",
  "source_count": 0,
  "target_count": 0,
  "diff_rows": 0,
  "diff_pct": 0.0,
  "target_source_ratio": 1.0,
  "mode": "exact",
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL",
  "notes": []
}
```

## Completion criterion

Complete when source and target counts were computed for equivalent partitions, zero-count and division-by-zero cases were handled explicitly, the selected threshold source is named, and the JSON result explains every WARN or FAIL.
