---
name: table-duplicate-check
kind: leaf
description: "Check row-level uniqueness in a target table by its natural key. Use when: duplicate detection, duplicate check, uniqueness check, duplicate rows. NOT for: null rates (table-null-check), row totals (table-row-count), source-target orphans (table-traceability-check), schema drift (table-schema-check), freshness (table-freshness-check), or distribution drift (table-distribution-check) - key uniqueness only."
---

# Data Duplicate Check - Row Uniqueness

Check row-level uniqueness in the target table by its natural key.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Target table name (Trino path)
- Partition filter
- Key expression (depends on table): a declared primary key, natural key, or composite key per table schema

## Query

```sql
SELECT
  COUNT(*)                                    AS total_rows,
  COUNT(DISTINCT <key_expression>)            AS distinct_keys,
  COUNT(*) - COUNT(DISTINCT <key_expression>) AS duplicate_rows
FROM <target_table>
WHERE <partition_filter>;
```

## Thresholds

| Condition | Outcome |
|-----------|---------|
| duplicate_rows = 0 | PASS |
| duplicate_rows > 0 | FAIL - investigate key derivation and upstream deduplication |

## Output

Return JSON:
```json
{
  "check": "duplicate_detection",
  "total_rows": 0,
  "distinct_keys": 0,
  "duplicate_rows": 0,
  "result": "PASS"
}
```
