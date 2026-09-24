---
name: table-distribution-check
kind: leaf
description: "Compare value-frequency distribution of a column between two tables - detect category drift, top-N reshuffle, or new/missing values. Use when: distribution shift, category drift, value distribution, top values diff, percentile drift, distribution skew. NOT for: schema changes (table-schema-check), null rates (table-null-check), or row totals (table-row-count) - value-frequency shape only."
---

# Data Distribution Check - Value Frequency Comparison

Compare the value-frequency distribution of a column between **baseline** and **test** tables for the same partition. Catches category drift that aggregate row counts miss.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Baseline table, test table (Trino paths)
- Partition filter
- Column or expression to compare (e.g. `outcome.source`, `signalsource`)
- Mode: `categorical` (default) or `numeric`

## Categorical Mode (string / enum columns)

Compute per-value share in each table, then full-outer-join on the value to surface shifts and new/missing categories.

```sql
WITH baseline AS (
  SELECT <col> AS val, COUNT(*) AS cnt
  FROM <baseline_table>
  WHERE <partition_filter>
  GROUP BY 1
),
test AS (
  SELECT <col> AS val, COUNT(*) AS cnt
  FROM <test_table>
  WHERE <partition_filter>
  GROUP BY 1
),
b_total AS (SELECT SUM(cnt) AS n FROM baseline),
t_total AS (SELECT SUM(cnt) AS n FROM test)
SELECT
  COALESCE(b.val, t.val) AS val,
  ROUND(100.0 * b.cnt / (SELECT n FROM b_total), 2) AS baseline_pct,
  ROUND(100.0 * t.cnt / (SELECT n FROM t_total), 2) AS test_pct,
  ROUND(100.0 * t.cnt / (SELECT n FROM t_total) - 100.0 * b.cnt / (SELECT n FROM b_total), 2) AS shift_pp
FROM baseline b
FULL OUTER JOIN test t ON b.val = t.val
ORDER BY ABS(shift_pp) DESC NULLS LAST;
```

## Numeric Mode (continuous columns)

Compare quantiles instead of values:

```sql
SELECT
  'baseline' AS source,
  approx_percentile(<col>, ARRAY[0.50, 0.90, 0.99]) AS p50_p90_p99
FROM <baseline_table>
WHERE <partition_filter>
UNION ALL
SELECT
  'test' AS source,
  approx_percentile(<col>, ARRAY[0.50, 0.90, 0.99])
FROM <test_table>
WHERE <partition_filter>;
```

## Thresholds

| Condition | Outcome |
|---|---|
| All categories \|shift_pp\| ≤ 2pp, no new/missing values | PASS |
| Any category 2pp < \|shift_pp\| ≤ 5pp | WARN |
| Any category \|shift_pp\| > 5pp | FAIL |
| Any baseline value missing from test (baseline_pct > 0.1%) | FAIL - category dropped |
| Any test value missing from baseline (test_pct > 0.1%) | FAIL - new category appeared |
| Numeric: any percentile shifts > 5% relative | WARN; > 10% | FAIL |


## Output

```json
{
  "check": "distribution",
  "column": "<col>",
  "mode": "categorical",
  "top_shifts": [
    {"val": "<v>", "baseline_pct": 0.0, "test_pct": 0.0, "shift_pp": 0.0},
    {"val": "<v>", "baseline_pct": 0.0, "test_pct": null, "shift_pp": null, "note": "missing in test"}
  ],
  "result": "PASS"
}
```
