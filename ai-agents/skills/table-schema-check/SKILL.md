---
name: table-schema-check
kind: leaf
description: "Detect schema drift between two tables - added/removed columns, type changes, nullable changes. Use when: schema drift, schema diff, column added, column removed, type change, schema comparison, schema validation. NOT for: value-level differences, distribution drift (table-distribution-check), row totals (table-row-count), null rates (table-null-check), duplicate keys (table-duplicate-check), freshness (table-freshness-check), or source-to-target traceability (table-traceability-check) - structure only."
---

# Data Schema Check - Column & Type Drift

Compare the column set and types between two tables (baseline vs test, or prior partition vs current). Catches drift that data-level checks miss.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Baseline table, test table (Trino paths)
- Optional: ignore-list of column-name prefixes (e.g. internal partition columns)

## Query - Trino `information_schema`

```sql
WITH baseline_cols AS (
  SELECT column_name, data_type, is_nullable
  FROM <catalog>.information_schema.columns
  WHERE table_schema = '<baseline_schema>' AND table_name = '<baseline_table>'
),
test_cols AS (
  SELECT column_name, data_type, is_nullable
  FROM <catalog>.information_schema.columns
  WHERE table_schema = '<test_schema>' AND table_name = '<test_table>'
)
SELECT
  COALESCE(b.column_name, t.column_name) AS column_name,
  b.data_type AS baseline_type,
  t.data_type AS test_type,
  b.is_nullable AS baseline_nullable,
  t.is_nullable AS test_nullable,
  CASE
    WHEN b.column_name IS NULL                                  THEN 'ADDED'
    WHEN t.column_name IS NULL                                  THEN 'REMOVED'
    WHEN b.data_type IS DISTINCT FROM t.data_type               THEN 'TYPE_CHANGED'
    WHEN b.is_nullable IS DISTINCT FROM t.is_nullable           THEN 'NULLABILITY_CHANGED'
    ELSE 'MATCH'
  END AS change_kind
FROM baseline_cols b
FULL OUTER JOIN test_cols t USING (column_name)
WHERE change_kind != 'MATCH'
ORDER BY change_kind, column_name;
```

For Hive/Iceberg tables where `information_schema` is incomplete, fall back to `DESCRIBE <table>` and compare row-by-row.

## Severity Rules

| change_kind | Outcome |
|---|---|
| `MATCH` (all columns) | PASS |
| `ADDED` (test has new column) | WARN - verify intentional; downstream consumers may ignore |
| `REMOVED` (baseline column missing in test) | FAIL - breaking change |
| `TYPE_CHANGED` (e.g. `varchar` → `bigint`) | FAIL |
| `NULLABILITY_CHANGED` (non-null → nullable) | WARN |
| `NULLABILITY_CHANGED` (nullable → non-null) | FAIL - backfill risk |

## Output

```json
{
  "check": "schema_drift",
  "changes": [
    {"column_name": "foo", "change_kind": "ADDED", "test_type": "varchar"},
    {"column_name": "bar", "change_kind": "TYPE_CHANGED", "baseline_type": "varchar", "test_type": "bigint"}
  ],
  "result": "PASS|WARN|FAIL"
}
```
