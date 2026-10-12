---
name: html-report
kind: leaf
description: "Use when: build a self-contained HTML review page - a plan, validation, or status report a human reads to decide something - for the user or for another skill that lists the page's questions. NOT for: serving or opening pages locally (local-server), markdown docs, slides, or spreadsheets."
---

# HTML review page

## Objective

Produce one HTML page that lets a reviewer answer the page's questions in under 2 minutes, and that a senior reviewer would choose over the markdown it summarizes. The questions come from the calling skill or the user; the page exists so a human can decide (approve, ship, fix) fast and trust what they decided on. The layouts and visuals below are defaults, not limits: IF a better structure or visual exists, use it.

## Guardrails & Constraints

- MUST be one self-contained file that works offline: inline CSS, inline SVG, and inline JS are all fine; no external scripts, fonts, CDNs, or images.
- MUST answer the page's main question at the top (status plus the few numbers that matter), before any detail.
- MUST make every number traceable to its source (a query, file, or run listed on the page), and never invent, estimate, or round away a value that drives the conclusion.
- MUST make status readable without color: pair every status color with a label or icon.
- MUST fold bulky detail (SQL, raw rows, file lists, logs) into collapsed `<details>` or an equivalent toggle.
- MUST NOT paste the source document (e.g. `plan.md`) into the page as the main content; summarize it visually and fold the source away.
- MUST keep secrets out of the page, and show record-level data only as far as the reviewer needs it.
- IF no caller lists the page's questions, MUST derive the main question and a few supporting ones from the request, and state them in an HTML comment at the top of the file.

## Preferences

- SHOULD let visuals carry the page: lead each part with a chart, diagram, tiles, matrix, or table, and keep text to short captions. SHOULD stay under about 150 words of prose; exceed it only when a visual cannot carry the point.
- SHOULD pick the visual that fits the data, e.g. tiles for headline numbers, bars for comparisons, box-and-arrow diagrams for flows, a heatmap or grid for many-by-many status, a timeline for dates or stages, or anything better.
- SHOULD add interactivity when it helps review: tabs, hover detail, sortable or filterable tables, toggles between views.
- SHOULD use one consistent status palette (e.g. green pass, amber warn or changed, red fail or risk, grey skipped or unchanged), label every chart (title, units, values, legend for multiple series), and fit the top section in one laptop screen.
- IF it departs from the caller's suggested layout, SHOULD say why in an HTML comment at the top of the file.

## Output

The page's absolute path.

## Verification

Before returning, open the page and check, then fix what fails:
- every question the caller lists (or the page's own comment states) can be answered from the page, and the main one from the top screen;
- it renders with the network off;
- no label clips or overlaps, and no chart is decorative only;
- every number on it traces to a listed source.

IF the host cannot render the page (no browser), check the HTML source for these instead, and report that the visual check (clipping, overlap) was not done.
