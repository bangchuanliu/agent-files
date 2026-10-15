# Prompt templates

Copy-paste-ready prompts for each step of the `tech-domain-dashboard` workflow. Fill in the
`{PLACEHOLDER}` slots. After a real run, save the filled-in version as
`<topic-slug>/PROMPT.md` next to that topic's `.md`/`.html`, plus a short "Notes from this
run" section noting anything you had to correct - this is what makes reapplying the
workflow to the next domain faster and more accurate than starting from scratch.

## Contents

- Filling in the placeholders
- PROMPT A: Research + markdown
- PROMPT B: Fact-check pass (run before building the HTML)
- PROMPT C: HTML dashboard conversion
- Short form (single message, when you trust the model to run the whole pipeline)

## Filling in the placeholders

- `{TOPIC}`: the domain name, e.g. "Attribution", "Rate limiting", "Feature stores".
- `{CONTEXT}`: one clause of context, e.g. "as a component of digital ads measurement" or
  "as a component of high-QPS backend systems".
- `{SUB_PROBLEM_1..N}`: 4-6 lines, each a genuinely hard sub-problem chosen per Step 1's
  three-part test in SKILL.md (structural cause + named solutions + real limitations).
- `{topic-slug}`: kebab-case filename stem, e.g. `attribution-deep-dive`.
- `{OUTPUT_DIR}`: the project's docs directory, e.g. `~/project/li-ads/ads-measurement-study`.

## PROMPT A: Research + markdown

```
Deep dive into "{TOPIC}" {CONTEXT}.

This is a read-only research task, not a code task - no need to read or modify any
repository's code.

For each of these core problems, explain:
(a) WHY the problem is structurally hard (root cause, not just symptom)
(b) What INDUSTRY-STANDARD solutions/approaches exist today (name specific vendors,
    products, algorithms, or papers - not generic categories)
(c) Known limitations/tradeoffs of those industry solutions

Cover these sub-problems:
1. {SUB_PROBLEM_1}
2. {SUB_PROBLEM_2}
3. {SUB_PROBLEM_3}
4. {SUB_PROBLEM_4}
5. {SUB_PROBLEM_5}
[6. {SUB_PROBLEM_6} - optional]

Be technically specific with concrete named companies/techniques/papers. Prefer citable,
checkable claims over impressive-sounding but unverifiable ones - if you're not confident a
product/paper name is real, say so explicitly rather than inventing one. Write a structured
report with headers per sub-problem, ~150-250 words each. No generic filler.

Save the report as {OUTPUT_DIR}/{topic-slug}/{topic-slug}.md (create the folder if needed).
No em dashes (U+2014) anywhere in the file - use a plain hyphen.
```

## PROMPT B: Fact-check pass (run before building the HTML)

```
Fact-check every named product, tool, statistic, and causal/mechanistic claim in
{OUTPUT_DIR}/{topic-slug}/{topic-slug}.md against what you actually know with confidence.
For each claim: confirm it (ideally with a citable source - a paper name + year, or a
vendor's own documentation page), correct it, or remove it if you cannot verify it. Add a
short References section listing citable sources with links where available. Report back
exactly what you changed and why, so nothing is silently rewritten.
```

## PROMPT C: HTML dashboard conversion

```
Convert {OUTPUT_DIR}/{topic-slug}/{topic-slug}.md into an interactive HTML study dashboard,
following the tech-domain-dashboard skill's HTML spec
(ai-agents/skills/experimental/tech-domain-dashboard/references/html-dashboard-spec.md in the agent-files repo):

- Single self-contained HTML file, vanilla JS, inline SVG, zero external dependencies (must
  work offline via file://).
- Tabs: Overview, one per sub-problem, Vendor/reference map, FAQ / Practice, Sync.
- Overview tab: KPI cards, a system/flow SVG diagram, one-line takeaway per sub-problem.
- Each sub-problem tab: an SVG diagram illustrating the mechanism, a "why hard" callout, and
  3-column why/solutions/limitations cards. Add an interactive control (slider, toggle,
  before/after switch) wherever the content has a real formula or comparison worth exploring
  live.
- Vendor/reference tab: named companies/tools/papers from the report, with links where
  citable, and an explicit "unverified" label on anything not fully confirmed.
- FAQ / Practice tab: 20-30 questions, each `{id, type, topic, level, q, look, a, f, p}`.
  Filters for type/topic/level, search, random-question button, expand/collapse, mark-done
  checkboxes, progress bar. Progress saved to localStorage under a stable per-item id.
- Sync tab: export progress as a copyable code, import (merge, not overwrite), reset.

Save as {OUTPUT_DIR}/{topic-slug}/{topic-slug}.html. Then add a card for it in
{OUTPUT_DIR}/index.html under "Deep dives" (or create that hub if it doesn't exist yet),
between the <!-- DASHBOARDS:START --> / <!-- DASHBOARDS:END --> markers, linking to
{topic-slug}/{topic-slug}.html and matching the existing card format and question count.

Verify before reporting done:
- Every tab switches, every SVG renders with no clipped/overlapping labels, no console
  errors.
- FAQ count, filters, random button, and mark-done all work.
- Sync export -> reset -> import round-trips progress correctly.
- The hub link resolves to the right relative path.
- Zero em dashes (U+2014) in both the .md and the .html:
  python3 -c "import sys;print(open(sys.argv[1]).read().count(chr(0x2014)))" <file>
  must print 0 for each file.
- If any sub-problem has an interactive control with a real formula, spot-check its output
  by hand at one boundary value.
- Flag any claim you could not verify or any product/paper name you're not confident is
  real, rather than silently keeping it.
```

## Short form (single message, when you trust the model to run the whole pipeline)

```
Use the tech-domain-dashboard skill to deep-dive into "{TOPIC}" ({CONTEXT}), covering:
1. {SUB_PROBLEM_1}
2. {SUB_PROBLEM_2}
3. {SUB_PROBLEM_3}
4. {SUB_PROBLEM_4}
5. {SUB_PROBLEM_5}
Output dir: {OUTPUT_DIR}/{topic-slug}/. Register in the hub index.html.
```
