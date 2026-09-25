---
name: table-distribution-check
kind: leaf
description: "Distribution check: compare value-frequency or numeric distribution for one column between two table slices. Use when: distribution shift, category drift, value distribution, top values diff, percentile drift, skew. NOT for: schema drift (table-schema-check), null rates (table-null-check), row totals (table-row-count), duplicate keys (table-duplicate-check), freshness (table-freshness-check), or source-target joins (table-traceability-check)."
---

# Table Distribution Check

Compare one column's distribution between baseline and test slices. Use categorical mode for enum or low-cardinality values, and numeric mode for continuous measures.

## Inputs

- Baseline table or subquery: `<baseline_table_or_subquery>`.
- Test table or subquery: `<test_table_or_subquery>`.
- Baseline and test partition filters. Use equivalent logical windows.
- Column or expression to compare, with a stable alias.
- Mode: `categorical` or `numeric`.
- Optional top-N limit for evidence, default 50.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific thresholds from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The queries below are ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

Categorical mode:

```sql
WITH baseline AS (
  SELECT <column_expression> AS val, COUNT(*) AS cnt
  FROM <baseline_table_or_subquery>
  WHERE <baseline_partition_filter>
  GROUP BY 1
),
test AS (
  SELECT <column_expression> AS val, COUNT(*) AS cnt
  FROM <test_table_or_subquery>
  WHERE <test_partition_filter>
  GROUP BY 1
),
totals AS (
  SELECT
    (SELECT SUM(cnt) FROM baseline) AS baseline_n,
    (SELECT SUM(cnt) FROM test) AS test_n
)
SELECT
  COALESCE(b.val, t.val) AS val,
  b.cnt AS baseline_count,
  t.cnt AS test_count,
  100.0 * COALESCE(b.cnt, 0) / NULLIF(totals.baseline_n, 0) AS baseline_pct,
  100.0 * COALESCE(t.cnt, 0) / NULLIF(totals.test_n, 0) AS test_pct,
  100.0 * COALESCE(t.cnt, 0) / NULLIF(totals.test_n, 0)
    - 100.0 * COALESCE(b.cnt, 0) / NULLIF(totals.baseline_n, 0) AS shift_pp
FROM baseline b
FULL OUTER JOIN test t
  ON b.val IS NOT DISTINCT FROM t.val
CROSS JOIN totals
ORDER BY ABS(shift_pp) DESC NULLS LAST, val
FETCH FIRST <top_n> ROWS ONLY;
```

Numeric mode:

```sql
SELECT
  'baseline' AS source,
  COUNT(*) AS row_count,
  AVG(<column_expression>) AS avg_value,
  approx_percentile(<column_expression>, ARRAY[0.50, 0.90, 0.99]) AS p50_p90_p99
FROM <baseline_table_or_subquery>
WHERE <baseline_partition_filter>
UNION ALL
SELECT
  'test' AS source,
  COUNT(*) AS row_count,
  AVG(<column_expression>) AS avg_value,
  approx_percentile(<column_expression>, ARRAY[0.50, 0.90, 0.99]) AS p50_p90_p99
FROM <test_table_or_subquery>
WHERE <test_partition_filter>;
```

If the engine lacks `approx_percentile`, use its nearest percentile function and state the substitution.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| Categorical: every value has `ABS(shift_pp) <= 2` and no new or missing material values | PASS |
| Categorical: any `2 < ABS(shift_pp) <= 5` | WARN |
| Categorical: any `ABS(shift_pp) > 5` | FAIL |
| Categorical: baseline value missing in test with `baseline_pct > 0.1` | FAIL |
| Categorical: test value missing in baseline with `test_pct > 0.1` | FAIL |
| Numeric: every tracked percentile shifts by `<= 5%` relative | PASS |
| Numeric: any percentile shifts by `> 5%` and `<= 10%` relative | WARN |
| Numeric: any percentile shifts by `> 10%` relative | FAIL |
| Either slice has zero rows | FAIL unless row-count or freshness checks established that an empty slice is expected |

## Output format

Return JSON:

```json
{
  "check": "distribution",
  "column": "<column_alias>",
  "mode": "categorical|numeric",
  "baseline_rows": 0,
  "test_rows": 0,
  "top_shifts": [
    {"val": "<v>", "baseline_pct": 0.0, "test_pct": 0.0, "shift_pp": 0.0, "note": ""}
  ],
  "percentiles": {},
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL"
}
```

## Completion criterion

Complete when the chosen mode matches the column type, baseline and test filters are recorded, zero-row slices are handled explicitly, top categorical shifts or numeric percentile shifts are included, and the JSON result explains every WARN or FAIL.
