---
name: study-dashboard
kind: leaf
description: Turn a system design or domain deep-dive topic into a self-contained, visual HTML study dashboard (diagrams, flows, charts, FAQ practice tab, progress sync) plus a markdown source, and register it in a hub index. Also builds question-bank dashboards (patterns x companies). Use when the user says "make a dashboard for a topic", "study dashboard", "deep dive into a design question with diagrams", "add a FAQ/practice tab", "question bank for a company or area", or "generate SD questions and a dashboard".
---

# study-dashboard

Produces reviewable study artifacts, not a live interview. Boundaries:
- `sysdesign-drill` = live, timed mock interview. `domain-drill` = Socratic questioning.
- `study-dashboard` = durable artifacts you re-read and self-test with on any device.

## Output location

Default dir: ask once, else `~/project/<area>/docs/` (e.g. `~/project/li-ads/ads-measurement-study`).
Filenames: kebab-case, `<topic>.md` + `<topic>.html`. The hub is `index.html` in the same dir.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| deep-dive | "deep dive / dashboard for <topic>" | `<topic>.md` + `<topic>.html` (tabs: Overview, one tab per sub-problem, FAQ, Sync) |
| question-bank | "SD questions for <area/companies>" | `<name>.html` from `assets/question-bank-template.html` (swap `P` and `C` data) |
| add-faq | "add FAQ/practice tab to <file>" | Adds FAQ tab to an existing dashboard |
| register | always, last step | Appends a card to `index.html` between `<!-- DASHBOARDS:START -->` / `<!-- DASHBOARDS:END -->` (create from `assets/index-template.html` if missing) |

## Workflow (deep-dive)

1. **Scope**: list 4-6 sub-problems. For each: (a) why structurally hard (root cause), (b) industry-standard solutions with named vendors/techniques, (c) limitations/tradeoffs. Parallelize research with explore/research agents, one per sub-problem.
2. **Markdown first**: write `<topic>.md` (150-250 words per sub-problem, no filler). This is the canonical text.
3. **HTML dashboard**: single file, vanilla JS, inline SVG, zero external deps (works offline / file://).
   - Tabs: `<nav id="nav"><button data-t="...">` + `<section id="...">`, switched by `show(t)`.
   - Per sub-problem tab: one SVG flow diagram (boxes + arrows via an `el(tag, attrs)` helper), a "why hard" callout, a solutions table (technique | vendor examples | tradeoff), and a small chart when numbers exist.
   - Overview tab: the full system map SVG, KPI cards, one-line takeaway per sub-problem.
   - Dark palette, consistent color per concept across all diagrams.
   Reference implementation (private, do not copy into this repo): `~/project/li-ads/ads-measurement-study/conversion-tracking/conversion-tracking-signals.html`.
4. **FAQ / practice tab** (20-30 items). Schema per item:
   `{id, type: 'design'|'deep-dive'|'tradeoff'|'debug', topic, level: 'L4'|'L5'|'L6', q, look /*what interviewer probes*/, a /*model answer bullets*/, f /*follow-ups*/, p /*pitfalls*/}`
   Features: filter chips (type/topic/level), "random question", expand-to-reveal answer, mark-done checkbox, progress bar. Progress in `localStorage` key `<slug>-done`.
5. **Sync tab**: export done-set as base64 code (copy button), import = merge, reset. Needed because localStorage is per device and per origin.
6. **Register** in `index.html` hub.
7. **Verify** (mandatory, not optional):
   - Serve: `python3 -m http.server 8765 --bind 127.0.0.1 --directory <dir>` (or the `local-server` skill) and open in the browser canvas.
   - `evaluate_javascript`: count SVGs per tab, FAQ items, check every cross-reference id resolves, round-trip export/import, no console errors.
   - Screenshot each tab and fix anything visually off (overlapping labels, clipped SVG text).
   - `python3 -c "import sys;print(open(sys.argv[1]).read().count(chr(0x2014)))" <file>` must print 0 (no em dashes; macOS bash 3.2 does not expand `$'\u...'`, so grep with it silently checks the wrong string).

## Workflow (question-bank)

Copy `assets/question-bank-template.html`, then replace only the data block at the top of the script:
- `P` = patterns: `{id, cat, lvl, name, q, tension, bote, flow:[steps], look, a:[], f:[], p:[]}`. `id` is a stable progress key; never rename after publishing.
- `C` = companies: `{Name: {blurb, qs: [[question, [patternIds], twist, level], ...]}}`.
The engine derives the pattern x company matrix, jump links, and progress. Verify that every pattern id referenced in `C` exists (`CQ.flatMap(c=>c.pats).filter(p=>!byId[p])` must be empty). Label company questions as "commonly reported themes, not verified".

## Sensitivity

Dashboards on employer-internal topics stay in private locations. Never place them in this public skills repo or public hosting. Scrub internal names, table names, and enums before any public share.

## Multi-device

Recommend: private git repo for the docs dir + access-controlled static hosting (Cloudflare Pages + Access, or Netlify password) with the hub as the one bookmark. Simplest fallback: iCloud/Dropbox folder. Progress moves between devices via the Sync tab codes.
