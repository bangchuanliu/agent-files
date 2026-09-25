---
name: table-schema-check
kind: leaf
description: "Schema check: detect structural drift between two tables, including added or removed columns, type changes, and nullability changes. Use when: schema drift, schema diff, column added, column removed, type change, schema comparison. NOT for: value-level differences, distribution drift (table-distribution-check), row totals (table-row-count), null rates (table-null-check), duplicate keys (table-duplicate-check), freshness (table-freshness-check), or source-target joins (table-traceability-check)."
---

# Table Schema Check

Compare column names, data types, and nullability between a baseline and test table. Use this for structure only; use data checks after structure passes.

## Inputs

- Baseline table: `<baseline_catalog>.<baseline_schema>.<baseline_table>`.
- Test table: `<test_catalog>.<test_schema>.<test_table>`.
- Optional ignore list for partition columns, metadata columns, or local internal prefixes.
- Optional expected changes, with ticket or migration reference when available.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific allowed changes from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The query below is ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

Use `information_schema` when reliable:

```sql
WITH baseline_cols AS (
  SELECT column_name, data_type, is_nullable
  FROM <baseline_catalog>.information_schema.columns
  WHERE table_schema = '<baseline_schema>'
    AND table_name = '<baseline_table>'
    AND column_name NOT IN (<ignored_columns>)
),
test_cols AS (
  SELECT column_name, data_type, is_nullable
  FROM <test_catalog>.information_schema.columns
  WHERE table_schema = '<test_schema>'
    AND table_name = '<test_table>'
    AND column_name NOT IN (<ignored_columns>)
),
diff AS (
  SELECT
    COALESCE(b.column_name, t.column_name) AS column_name,
    b.data_type AS baseline_type,
    t.data_type AS test_type,
    b.is_nullable AS baseline_nullable,
    t.is_nullable AS test_nullable,
    CASE
      WHEN b.column_name IS NULL THEN 'ADDED'
      WHEN t.column_name IS NULL THEN 'REMOVED'
      WHEN b.data_type IS DISTINCT FROM t.data_type THEN 'TYPE_CHANGED'
      WHEN b.is_nullable IS DISTINCT FROM t.is_nullable THEN 'NULLABILITY_CHANGED'
      ELSE 'MATCH'
    END AS change_kind
  FROM baseline_cols b
  FULL OUTER JOIN test_cols t USING (column_name)
)
SELECT *
FROM diff
WHERE change_kind <> 'MATCH'
ORDER BY change_kind, column_name;
```

If `information_schema` is incomplete, run the local equivalent of `DESCRIBE <table>` for both tables and compare the same fields. Preserve case-sensitivity rules from the engine.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| No rows returned by the diff query | PASS |
| `ADDED` column is documented as expected | WARN |
| `ADDED` column is undocumented | WARN |
| `REMOVED` column | FAIL |
| `TYPE_CHANGED` | FAIL |
| `NULLABILITY_CHANGED` from non-null to nullable | WARN |
| `NULLABILITY_CHANGED` from nullable to non-null | FAIL unless an expected backfill and compatibility plan are documented |
| Any expected change without a matching diff row | WARN |

## Output format

Return JSON:

```json
{
  "check": "schema_drift",
  "baseline_table": "<baseline_catalog>.<baseline_schema>.<baseline_table>",
  "test_table": "<test_catalog>.<test_schema>.<test_table>",
  "ignored_columns": [],
  "changes": [
    {"column_name": "foo", "change_kind": "ADDED", "test_type": "varchar"},
    {"column_name": "bar", "change_kind": "TYPE_CHANGED", "baseline_type": "varchar", "test_type": "bigint"}
  ],
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL"
}
```

## Completion criterion

Complete when baseline and test schemas were compared with the same ignore rules, every schema diff is classified, expected changes are reconciled, fallback metadata sources are named if used, and the JSON result explains every WARN or FAIL.
