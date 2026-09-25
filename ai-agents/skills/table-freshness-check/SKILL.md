---
name: table-freshness-check
kind: leaf
description: "Freshness check: verify the latest partition is on-time and non-empty against its SLA. Use when: freshness check, SLA, latest partition, partition lag, table staleness, data delay, partition not landed. NOT for: content correctness after landing, row totals (table-row-count), null rates (table-null-check), duplicate keys (table-duplicate-check), schema drift (table-schema-check), distribution drift (table-distribution-check), or source-target joins (table-traceability-check)."
---

# Table Freshness Check

Verify that the latest partition has landed within its SLA and has enough rows to be usable. Use this before relying on a table as an input, or for oncall freshness triage.

## Inputs

- Target table: `<target_table>`.
- Partition column: `<partition_col>`, default `datepartition` when local conventions say so.
- Partition cadence: daily, hourly, or another declared cadence.
- SLA in hours after partition close. Example: daily SLA 4h means partition `D` is due at `D+1 04:00 UTC`.
- Optional minimum row threshold for a landed partition.
- Optional partition filter limiting valid partitions, such as excluding backfill or test partitions.
- Optional context overrides: if a local `table-checks/context.md` exists, use table-specific SLA and row thresholds from it and cite them in the output. Its absence is normal.
- SQL engine: run with whatever SQL engine or tool is available in this environment. Engine, catalog, cluster, and credential details come from local context. The query below is ANSI/Trino-flavoured; adapt only syntax, not semantics.

## Query

```sql
WITH latest AS (
  SELECT MAX(<partition_col>) AS latest_partition
  FROM <target_table>
  WHERE <valid_partition_filter>
)
SELECT
  l.latest_partition,
  COUNT(t.<partition_col>) AS row_count
FROM latest l
LEFT JOIN <target_table> t
  ON t.<partition_col> = l.latest_partition
 AND <valid_partition_filter_for_t>
GROUP BY l.latest_partition;
```

Compute lag outside SQL if partition parsing is environment-specific:

```text
partition_close_time = close time implied by latest_partition and cadence
lag_hours = (current_utc_time - partition_close_time) / 1 hour
```

For engines with reliable timestamp parsing, the lag calculation may be done in SQL. Keep timezone explicit and use UTC unless local context says otherwise.

## Interpretation and thresholds

| Condition | Outcome |
|---|---|
| `latest_partition` exists, `lag_hours <= sla_hours`, and `row_count >= min_rows` | PASS |
| `latest_partition` is null | FAIL |
| `lag_hours <= sla_hours` and `row_count < min_rows` | FAIL |
| `sla_hours < lag_hours <= 2 * sla_hours` | WARN |
| `lag_hours > 2 * sla_hours` | FAIL |
| Landed partition has zero rows | FAIL |

A landed-but-empty partition is a failure because the pipeline produced an unusable slice.

## Output format

Return JSON:

```json
{
  "check": "freshness",
  "partition_col": "<partition_col>",
  "latest_partition": "2026-05-14",
  "cadence": "daily",
  "partition_close_time_utc": "2026-05-15T00:00:00Z",
  "lag_hours": 3.2,
  "sla_hours": 4,
  "row_count": 12345678,
  "min_rows": 1,
  "threshold_source": "default|local_context",
  "result": "PASS|WARN|FAIL",
  "notes": []
}
```

## Completion criterion

Complete when the latest valid partition and row count were measured, cadence and UTC close-time assumptions are explicit, SLA and minimum-row threshold sources are named, and the JSON result explains every WARN or FAIL.
