---
name: table-null-check
kind: leaf
description: "Null check: compute null-rate per critical column, optionally diffing against a baseline. Use when: null rate, null check, missing values, column completeness, null shift. NOT for: row totals (table-row-count), duplicate keys (table-duplicate-check), schema drift (table-schema-check), freshness (table-freshness-check), distribution drift (table-distribution-check), or source-target joins (table-traceability-check)."
---

# Table Null Check

Compute null rates for critical columns in one table, or compare null rates between baseline and test slices. Use this for column completeness, not row volume or schema existence.

## Inputs

- Target table: `<target_table>`.
- Target partition filter: `<target_partition_filter>`.
- Column list or expressions. Use stable aliases for expressions.
- Column contract: nullable, non-nullable, primary key, or informational.
- Optional baseline table and baseline partition filter for diff mode.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific thresholds from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The query below is ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

Run once per column or expression. Keep the alias stable in the output.

```sql
SELECT
  '<column_alias>' AS column_name,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN <column_expression> IS NULL THEN 1 ELSE 0 END) AS null_count,
  100.0 * SUM(CASE WHEN <column_expression> IS NULL THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0) AS null_pct
FROM <target_table>
WHERE <target_partition_filter>;
```

Diff mode:

```sql
WITH baseline AS (
  SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN <baseline_column_expression> IS NULL THEN 1 ELSE 0 END) AS null_count
  FROM <baseline_table>
  WHERE <baseline_partition_filter>
),
test AS (
  SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN <test_column_expression> IS NULL THEN 1 ELSE 0 END) AS null_count
  FROM <target_table>
  WHERE <target_partition_filter>
)
SELECT
  '<column_alias>' AS column_name,
  100.0 * b.null_count / NULLIF(b.total_rows, 0) AS baseline_null_pct,
  100.0 * t.null_count / NULLIF(t.total_rows, 0) AS test_null_pct,
  100.0 * t.null_count / NULLIF(t.total_rows, 0)
    - 100.0 * b.null_count / NULLIF(b.total_rows, 0) AS diff_pp,
  b.total_rows AS baseline_rows,
  t.total_rows AS test_rows
FROM baseline b
CROSS JOIN test t;
```

Nested fields are engine-specific. Use the local engine's field access syntax while preserving `IS NULL` semantics.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| Declared non-nullable column has `null_count = 0` | PASS |
| Declared non-nullable column has `null_count > 0` | FAIL |
| Primary key column moves from 0 nulls to any nulls | FAIL |
| Diff mode: `ABS(diff_pp) <= 0.1` | PASS |
| Diff mode: `0.1 < ABS(diff_pp) <= 1.0` | WARN |
| Diff mode: `ABS(diff_pp) > 1.0` | FAIL |
| `total_rows = 0` | FAIL unless the row-count check established that an empty slice is expected |

## Output format

Return JSON, one entry per checked column:

```json
{
  "check": "null_rate",
  "partition_filter": "<target_partition_filter>",
  "results": [
    {
      "column": "<column_alias>",
      "contract": "non_nullable|primary_key|nullable|informational",
      "total_rows": 0,
      "null_count": 0,
      "null_pct": 0.0,
      "baseline_null_pct": null,
      "test_null_pct": null,
      "diff_pp": null,
      "result": "PASS|WARN|FAIL"
    }
  ],
  "threshold_source": "default|local_context"
}
```

## Completion criterion

Complete when every requested column has a result, empty-slice behaviour is reconciled with the row-count check or marked FAIL, baseline and test filters are shown for diff mode, and the JSON result explains every WARN or FAIL.
