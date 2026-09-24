---
name: table-freshness-check
kind: leaf
description: "Verify the latest partition of a table is on-time, complete, and meets its SLA. Use when: freshness check, SLA, latest partition, partition lag, table staleness, data delay, partition not landed. NOT for: content correctness of a landed partition, row totals (table-row-count), null rates (table-null-check), duplicate keys (table-duplicate-check), schema drift (table-schema-check), distribution drift (table-distribution-check), or source-to-target traceability (table-traceability-check) - timeliness and completeness of the latest partition only."
---

# Data Freshness Check - Partition SLA

Verify a table's latest partition has landed within its SLA and contains rows. Use for oncall, daily monitoring, or before relying on a table as a join input.

## Step 0: Optional Context Overrides

If `~/.config/dotfiles/context/table-checks/context.md` exists, it may define table-specific threshold overrides for this table-check family. Read it and prefer its thresholds for the tables it names. Its absence is normal; the defaults below are complete on their own.

## Input

- Target table (Trino path)
- Partition column name (default `datepartition`)
- SLA in hours after partition wall-clock close (e.g. `daily, SLA 4h` means partition `D` must land by `D+1 04:00 UTC`)
- Optional: minimum row count threshold

## Query

```sql
-- Latest partition + its row count
SELECT
  MAX(<partition_col>) AS latest_partition,
  COUNT(*) AS row_count_for_latest
FROM <target_table>
WHERE <partition_col> = (SELECT MAX(<partition_col>) FROM <target_table>);
```

Compute lag in the orchestrator:
```
lag_hours = (NOW_UTC - partition_close_time(latest_partition)) / 1 hour
```
where `partition_close_time(D) = D + 1 day` for daily tables (the partition becomes "due" at the start of the next day) and `D + 1 hour` for hourly tables.

## Thresholds

| Condition | Outcome |
|---|---|
| `lag_hours ≤ SLA_hours` AND `row_count ≥ min_rows` | PASS |
| `lag_hours ≤ SLA_hours` AND `row_count < min_rows` | FAIL - partition landed but empty/short |
| `SLA_hours < lag_hours ≤ 2 × SLA_hours` | WARN |
| `lag_hours > 2 × SLA_hours` | FAIL - significant staleness |

A "landed" partition with zero rows is a FAIL, not a WARN — empty partitions usually indicate upstream pipeline failure that succeeded the partition write.

## Output

```json
{
  "check": "freshness",
  "latest_partition": "2026-05-14",
  "lag_hours": 3.2,
  "sla_hours": 4,
  "row_count": 12345678,
  "min_rows": 1000000,
  "result": "PASS"
}
```
