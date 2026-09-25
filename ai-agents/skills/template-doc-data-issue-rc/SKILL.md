---
name: template-doc-data-issue-rc
kind: leaf
description: "Data RCA doc: write or review a query-backed investigation narrative for a count discrepancy, parity gap, pipeline anomaly, or data incident. Branches: author from evidence; review an existing doc. NOT for: rendering check results, root-cause spreadsheets, entity-level RC assignment, or ship/hold readouts."
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
