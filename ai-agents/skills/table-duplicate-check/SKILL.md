---
name: table-duplicate-check
kind: leaf
description: "Duplicate check: verify row-level uniqueness by natural key in one table slice. Use when: duplicate detection, uniqueness check, duplicate rows, key collisions. NOT for: null rates (table-null-check), row totals (table-row-count), source-target orphans (table-traceability-check), schema drift (table-schema-check), freshness (table-freshness-check), or distribution drift (table-distribution-check)."
---

# Table Duplicate Check

Verify that a table slice has one row per natural key. Use this for key uniqueness only; use `table-traceability-check` for source-to-target orphan or coverage joins.

## Inputs

- Target table: `<target_table>`.
- Partition filter: `<partition_filter>`.
- Key expression: declared primary key, natural key, or composite key.
- Optional filters that define the validated population.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific thresholds from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The query below is ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

Prefer a grouped query so null keys and example duplicates are visible. For composite keys, set `<key_columns>` to the full component list, set `<null_key_predicate>` to any required component being null, and group by every component rather than concatenating strings.

```sql
WITH keyed AS (
  SELECT
    <key_columns>,
    COUNT(*) AS rows_per_key
  FROM <target_table>
  WHERE <partition_filter>
    AND <optional_filter>
  GROUP BY <key_columns>
),
summary AS (
  SELECT
    SUM(rows_per_key) AS total_rows,
    COUNT(*) AS distinct_keys,
    SUM(CASE WHEN rows_per_key > 1 THEN rows_per_key - 1 ELSE 0 END) AS duplicate_rows,
    SUM(CASE WHEN <null_key_predicate> THEN rows_per_key ELSE 0 END) AS null_key_rows,
    SUM(CASE WHEN rows_per_key > 1 THEN 1 ELSE 0 END) AS duplicate_key_count
  FROM keyed
)
SELECT
  total_rows,
  distinct_keys,
  duplicate_rows,
  duplicate_key_count,
  null_key_rows,
  100.0 * duplicate_rows / NULLIF(total_rows, 0) AS duplicate_pct
FROM summary;
```

Optional evidence query:

```sql
SELECT <key_columns>, rows_per_key
FROM keyed
WHERE rows_per_key > 1 OR <null_key_predicate>
ORDER BY rows_per_key DESC
FETCH FIRST 50 ROWS ONLY;
```

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| `duplicate_rows = 0` and `null_key_rows = 0` | PASS |
| `duplicate_rows > 0` | FAIL |
| `null_key_rows > 0` for a required key | FAIL |
| `total_rows = 0` | FAIL unless the row-count or freshness check established that an empty slice is expected |

## Output format

Return JSON:

```json
{
  "check": "duplicate_detection",
  "key_expression": "<key_expression>",
  "total_rows": 0,
  "distinct_keys": 0,
  "duplicate_rows": 0,
  "duplicate_key_count": 0,
  "null_key_rows": 0,
  "duplicate_pct": 0.0,
  "sample_duplicate_keys": [],
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL"
}
```

## Completion criterion

Complete when the natural key is named, duplicates and null-key rows are counted separately, partition filters are recorded, up to 50 duplicate examples are included when present, and the JSON result explains every WARN or FAIL.
