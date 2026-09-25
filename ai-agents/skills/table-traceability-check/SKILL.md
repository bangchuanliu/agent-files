---
name: table-traceability-check
kind: leaf
description: "Traceability check: verify source-target join integrity with orphan, coverage, and field-level mismatch checks. Use when: orphan detection, coverage check, source target traceability, field mismatch, key integrity. NOT for: aggregate counts (table-row-count), duplicate keys within one table (table-duplicate-check), null rates (table-null-check), schema drift (table-schema-check), freshness (table-freshness-check), or distribution drift (table-distribution-check)."
---

# Table Traceability Check

Verify that records trace between source and target through keys, and that mapped fields retain expected values. Use this after row-count and schema checks when record-level integrity matters.

## Inputs

- Source table or subquery: `<source_table_or_subquery>`.
- Target table or subquery: `<target_table_or_subquery>`.
- Source and target partition filters. Use equivalent logical windows.
- Join condition and explicit source and target join-key columns.
- Mapped fields for field-level integrity, with transformations documented when values are not expected to be identical.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific tolerances from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The queries below are ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

Orphan detection: every target record should trace to source.

```sql
SELECT COUNT(*) AS orphan_count
FROM <target_table_or_subquery> t
LEFT JOIN <source_table_or_subquery> s
  ON <join_condition>
 AND <source_partition_filter_in_join_if_needed>
WHERE <target_partition_filter>
  AND s.<source_join_key> IS NULL;
```

Coverage: every source record should appear in target.

```sql
WITH source_rows AS (
  SELECT COUNT(*) AS source_count
  FROM <source_table_or_subquery>
  WHERE <source_partition_filter>
),
missing AS (
  SELECT COUNT(*) AS missing_count
  FROM <source_table_or_subquery> s
  LEFT JOIN <target_table_or_subquery> t
    ON <join_condition>
   AND <target_partition_filter_in_join_if_needed>
  WHERE <source_partition_filter>
    AND t.<target_join_key> IS NULL
)
SELECT
  missing.missing_count,
  source_rows.source_count,
  100.0 * missing.missing_count / NULLIF(source_rows.source_count, 0) AS missing_pct
FROM missing
CROSS JOIN source_rows;
```

Field-level integrity: matched records should have expected values. Use `IS DISTINCT FROM` so null-safe differences are counted correctly.

```sql
SELECT
  COUNT(*) AS total_matched,
  SUM(CASE WHEN s.<source_field> IS DISTINCT FROM t.<target_field> THEN 1 ELSE 0 END) AS field_mismatch_count,
  100.0 * SUM(CASE WHEN s.<source_field> IS DISTINCT FROM t.<target_field> THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0) AS field_mismatch_pct
FROM <source_table_or_subquery> s
INNER JOIN <target_table_or_subquery> t
  ON <join_condition>
WHERE <source_partition_filter>
  AND <target_partition_filter>;
```

Repeat the field-level query per mapped field, or generate one query with one mismatch expression per field.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| `orphan_count = 0` | PASS for orphan check |
| `orphan_count > 0` | FAIL for orphan check |
| `missing_count = 0` | PASS for coverage check |
| `missing_pct <= 0.001` | WARN for coverage check |
| `missing_pct > 0.001` | FAIL for coverage check |
| Field mismatch count is 0 for every mapped field | PASS for field check |
| Any field mismatch rate `<= 0.001%` | WARN for field check |
| Any field mismatch rate `> 0.001%` | FAIL for field check |
| `source_count = 0` or `total_matched = 0` | FAIL unless row-count or freshness checks established that an empty slice is expected |

## Output format

Return JSON:

```json
{
  "check": "traceability",
  "join_condition": "<join_condition>",
  "orphan": {"orphan_count": 0, "result": "PASS|WARN|FAIL"},
  "coverage": {"source_count": 0, "missing_count": 0, "missing_pct": 0.0, "result": "PASS|WARN|FAIL"},
  "field_integrity": [
    {"field": "<field_name>", "total_matched": 0, "mismatch_count": 0, "mismatch_pct": 0.0, "result": "PASS|WARN|FAIL"}
  ],
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL"
}
```

## Completion criterion

Complete when orphan, coverage, and each requested field-level check were run or explicitly marked not applicable, source and target filters are recorded, null-safe comparisons are used for field mismatches, empty-slice cases are handled explicitly, and the JSON result explains every WARN or FAIL.
