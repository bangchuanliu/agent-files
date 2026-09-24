---
name: table-traceability-check
kind: leaf
description: "Verify source-target traceability - orphan detection, coverage, field-level integrity. Use when: orphan detection, coverage check, field mismatch. NOT for: aggregate counts (table-row-count), duplicate keys (table-duplicate-check), null rates (table-null-check), schema drift (table-schema-check), freshness (table-freshness-check), or distribution drift (table-distribution-check) - source-to-target join integrity only."
---

# Data Traceability - Orphan, Coverage, Field Integrity

Three sub-checks to verify every record traces correctly between source and target.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Source table/subquery, target table
- Join condition, partition filters
- Mapped fields (for 3c)

## Check 3a: Orphan Detection

Every target record must exist in source.

```sql
SELECT COUNT(*) AS orphan_count
FROM <target_table> t
LEFT JOIN <source_table_or_subquery> s ON <join_condition>
WHERE <target_partition_filter> AND s.<join_key> IS NULL;
```

| Condition | Outcome |
|-----------|---------|
| orphan_count = 0 | PASS |
| orphan_count > 0 | FAIL |

## Check 3b: Coverage

Every source record must appear in target.

```sql
SELECT COUNT(*) AS missing_count
FROM <source_table_or_subquery> s
LEFT JOIN <target_table> t ON <join_condition>
WHERE <source_partition_filter> AND t.<join_key> IS NULL;
```

| Condition | Outcome |
|-----------|---------|
| missing_count = 0 | PASS |
| missing_count <= 0.001% of source | WARN |
| missing_count > 0.001% of source | FAIL |

## Check 3c: Field-Level Integrity

Matched records must have identical values. Use `IS DISTINCT FROM` (not `!=`).

```sql
SELECT
  COUNT(*) AS total_matched,
  SUM(CASE WHEN s.<field> IS DISTINCT FROM t.<field> THEN 1 ELSE 0 END) AS <field>_mismatch
FROM <source> s
INNER JOIN <target> t ON <join_condition>
WHERE <partition_filters>;
```

| Condition | Outcome |
|-----------|---------|
| All mismatch = 0 | PASS |
| Any mismatch <= 0.001% | WARN |
| Any mismatch > 0.001% | FAIL |

## Output

Return JSON:
```json
{
  "check_3a": {"orphan_count": 0, "result": "PASS"},
  "check_3b": {"missing_count": 0, "result": "PASS"},
  "check_3c": {"mismatches": {}, "result": "PASS"}
}
```
