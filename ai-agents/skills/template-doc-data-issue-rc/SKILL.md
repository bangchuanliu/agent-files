---
name: template-doc-data-issue-rc
kind: leaf
description: "Write or review a data investigation / RCA write-up - count discrepancy, parity gap, pipeline anomaly, oncall data incident. Use when: data investigation doc, investigation write-up, RCA, root cause doc, discrepancy doc, parity gap report, why did counts drop, write up findings, postmortem for data issue, review my investigation doc. NOT for: rendering precomputed check results, building the root-cause evidence spreadsheet, assigning root causes to entities, or a ship/hold decision document - this is the written narrative only."
---

# Data Investigation Doc

Produce (or review) a written data investigation document with an answer-first structure
and query-backed evidence.

**Scope:** written investigation/analysis docs only. Not code, tests, config, design docs,
or runbooks.

## Process

1. Read `TEMPLATE.md` in this skill directory - it is the canonical structure.
2. Fill sections in this order: gather Evidence (§4) → derive Root Cause (§5) →
   quantify Impact (§6) → **write TLDR (§1) last** but place it first.
3. For every claim, attach the exact query with fully-qualified table name and
   partition/date filter. No query, no claim.
4. Run the magnitude check: does the stated root cause account for the full observed
   delta? State any unexplained residual explicitly.
5. List hypotheses ruled out, with how each was tested.
6. Label confidence (High/Medium/Low) and record what was **not** checked.

## Review mode

When asked to review an existing investigation doc, check it against the template's
section list and anti-patterns, and report: missing sections, unquantified claims,
evidence without reproducible queries, table names lacking DB prefix or date range,
correlation stated as causation, and missing magnitude check.

## Related

- Use a data-validation readout skill, if your environment supplies one, when the work ends in a ship/hold decision about data.
- `template-general-readout` - genre skeletons for non-data readouts.
- Use relevant validation or comparison skills to produce the evidence this doc consumes.
- Use notebook or report-rendering skills for appendix result sets when available.
