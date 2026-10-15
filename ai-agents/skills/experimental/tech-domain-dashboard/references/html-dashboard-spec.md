# HTML dashboard spec

Full structural spec for the self-contained HTML artifact built in Step 5 of the
`tech-domain-dashboard` skill. This is copy-adaptable, not copy-paste-exact - adjust colors,
counts, and diagram content to the topic, but keep the shape (tabs, card layout, FAQ schema,
Sync mechanics) consistent so every dashboard you build feels like the same tool.

## Contents

- File shape
- Layout skeleton
- Palette (adapt colors, keep the roles)
- Components
- FAQ / Practice tab
- Sync tab
- Minimal hub (`index.html`)

## File shape

Single `.html` file. Inline `<style>` and `<script>`, no external CSS/JS/font/CDN
dependencies - it must render correctly opened directly via `file://`, with no build step and
no network access.

## Layout skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{Topic} - Deep Dive</title>
<style>/* see Palette + Components below */</style>
</head>
<body>
<header>
  <h1>{Topic}</h1>
  <p>{one-line description}</p>
  <nav id="nav"><!-- one <button data-t="tabid"> per tab --></nav>
</header>
<main>
  <section id="overview" class="active">...</section>
  <section id="p1">...</section>
  <section id="p2">...</section>
  <!-- one section per sub-problem -->
  <section id="vendors">...</section>
  <section id="faq">...</section>
  <section id="sync">...</section>
</main>
<script>/* see Script below */</script>
</body>
</html>
```

Tab switching: clicking a `nav button` sets `.active` on the matching `button` and `section`,
removes it from all siblings. Keep this in one small `show(tabId)` function.

## Palette (adapt colors, keep the roles)

Use CSS custom properties for a consistent role-based palette across all diagrams and cards
in the file - not necessarily this exact palette, but keep semantic roles distinct:

```css
:root {
  --bg: #f5f7fa; --card: #ffffff; --ink: #1d2433; --muted: #5b6475; --line: #dde2ea;
  --blue: #0a66c2; --blue-soft: #e8f1fb;   /* neutral/info */
  --red: #c9372c; --red-soft: #fdeceb;     /* "why it's hard" */
  --green: #1f845a; --green-soft: #e6f4ee; /* "industry solutions" */
  --amber: #b86e00; --amber-soft: #fff4e0; /* "limitations" */
  --purple: #6e4bd8; --purple-soft: #efeafd; /* secondary/vendor */
}
```

## Components

**Overview tab**: KPI/stat cards in a `.kpis` grid (one per sub-problem, clickable to jump to
that tab), a system/flow SVG diagram showing how the sub-problems relate, and a one-line
takeaway per sub-problem.

**Sub-problem tab** (one per sub-problem, repeat structure): an SVG diagram illustrating the
mechanism (see SVG helper below), then a 3-column `.grid3` of cards:

```css
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 900px) { .grid3 { grid-template-columns: 1fr; } }
.col-why { border-top: 4px solid var(--red); }   .col-why h3 { color: var(--red); }
.col-sol { border-top: 4px solid var(--green); } .col-sol h3 { color: var(--green); }
.col-lim { border-top: 4px solid var(--amber); } .col-lim h3 { color: var(--amber); }
```

Column 1 = why it's hard, column 2 = industry solutions (as a bullet list or small table:
technique | vendor examples | tradeoff), column 3 = limitations. Add one interactive control
(a slider, a before/after toggle, a strategy switch) wherever the sub-problem has a real
formula or a real comparison worth exploring live - this is what makes practice sessions
stick versus a static page. Verify any such control computes the right number by hand at at
least one boundary value.

**SVG diagram helper**: a small `el(tag, attrs, children)` JS helper that builds SVG nodes
without a templating library, used for flow boxes + arrows:

```js
function el(tag, attrs={}, kids=[]) {
  const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  (Array.isArray(kids) ? kids : [kids]).forEach(k => k && n.appendChild(k));
  return n;
}
```

Keep diagram text short enough that labels don't clip at the box width you chose - this is
the most common visual bug; check it explicitly in verification (Step 7 of SKILL.md).

**Vendor/reference tab**: a list or small map of every named company/tool/paper from the
markdown, each with a link where the source is citable (vendor docs, paper landing page,
GitHub repo). Label anything the research pass wasn't fully sure of as "unverified" rather
than omitting the caveat.

## FAQ / Practice tab

Data shape per item (JS array literal, one array for the whole file):

```js
const FAQ = [
  { id: 'p1-q1', type: 'design', topic: 'sub-problem-1', level: 'L5',
    q: 'The question text.',
    look: 'What an interviewer/reader is actually probing for.',
    a: ['Model answer bullet 1', 'Model answer bullet 2'],
    f: ['A natural follow-up question'],
    p: ['A common pitfall/wrong answer'] },
  // 20-30 items total, spread across sub-problems and a mix of levels
];
```

`type` values: `design | deep-dive | tradeoff | debug`. `level`: whatever scale fits the
domain (e.g. `L4/L5/L6` for eng seniority, or a simpler `beginner/intermediate/advanced`).
`id` must be stable once published - it is the localStorage key, so renaming it loses a
user's progress.

Features required in this tab: filter chips for type/topic/level, a text search box, a
"random question" button, click-to-expand (question collapsed, click reveals `look`/`a`/`f`/
`p`), a mark-done checkbox per item, and a progress bar (`done / total`). Store done-state in
`localStorage` under a key like `<topic-slug>-done`, as a JSON array or object of `id`s.

## Sync tab

Because `localStorage` is per-browser-per-origin, add a manual sync mechanism:

- **Export**: read the done-set from `localStorage`, base64-encode it, show it in a
  read-only textarea with a copy button.
- **Import**: a textarea + button that decodes a pasted code and **merges** (union, never
  overwrites) it into the current done-set.
- **Reset**: a confirm-guarded button that clears the done-set.

Round-trip this manually during verification: export, clear via reset, import the exported
code back in, confirm the same items show as done.

## Minimal hub (`index.html`)

If the output directory doesn't have a hub yet, create one:

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Study dashboards</title>
<style>
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f7fa;color:#1d2433}
header{background:#0b1f3a;color:#fff;padding:22px 24px}h1{margin:0;font-size:22px}
main{max-width:900px;margin:0 auto;padding:20px 16px}
a.card{display:block;background:#fff;border:1px solid #dde2ea;border-left:4px solid #0a66c2;border-radius:10px;padding:14px 18px;margin-bottom:12px;color:inherit;text-decoration:none}
a.card b{color:#0a66c2}.m{color:#5b6475;font-size:13px}
</style></head><body>
<header><h1>Study dashboards</h1></header>
<main>
<!-- DASHBOARDS:START -->
<a class="card" href="{topic-slug}/{topic-slug}.html"><b>{Topic}</b><div class="m">{one-line summary + question count}</div></a>
<!-- DASHBOARDS:END -->
</main></body></html>
```

New entries go between the `DASHBOARDS:START` / `DASHBOARDS:END` comments, in the same
`<a class="card">` format, with the href relative to the hub's own location (e.g.
`{topic-slug}/{topic-slug}.html` if each topic lives in its own subfolder).
