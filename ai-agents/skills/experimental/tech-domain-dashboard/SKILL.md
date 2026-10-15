---
name: tech-domain-dashboard
kind: leaf
description: Turn any domain or topic into a durable study dashboard by systematically identifying its 4-6 genuinely hard sub-problems (not just sub-features), researching each one with named industry-standard solutions and real tradeoffs, writing a markdown source of truth, fact-checking it, and building a matching self-contained interactive HTML practice dashboard (diagrams, FAQ practice tab, cross-device progress sync), registered in a hub index. Use whenever the user asks to "deep dive into a topic", find the "core problems" or "hard problems" in a domain, "make a dashboard for a topic", explain why something is structurally hard plus how industry solves it, or wants to reapply this exact workflow to a new subject area (system design domains, ML infra, distributed systems, ads tech, or any other field) after already using it once.
---

# tech-domain-dashboard

Produces a durable, two-artifact study pair for one domain: a markdown report that is the
editable source of truth, and a self-contained HTML dashboard you practice against. The
markdown captures *why the domain is hard and what industry actually does about it*; the
HTML turns that into diagrams, worked examples, and a spaced-practice FAQ tab.

This is fully self-contained - it does not depend on any other skill. If a similar skill
(e.g. `study-dashboard`) is also installed, prefer whichever one the user names explicitly;
otherwise this one owns the full pipeline end to end.

## When this is the right shape

Good fits: any domain that decomposes into a handful of *structurally hard* problems, each
with real industry solutions and real tradeoffs - ads measurement, distributed systems
topics (consensus, caching, rate limiting), ML infra (feature stores, online serving), org
processes (incident response, on-call), anything with a "why is this hard / what does
industry do / what's the catch" shape.

Bad fits: a single narrow question with one right answer, a live timed interview drill (use
a Socratic/drill-style skill instead), or something you want as a one-off answer rather than
a durable file you'll revisit.

## Step 1: Scope - pick the sub-problems

This is the step that most determines quality, and it is judgment, not a template fill-in.
Do not default to generic sub-features ("basics", "advanced topics", "best practices").
Instead, propose 4-6 candidates and keep only the ones that pass all three tests:

(a) **Structural root cause.** You can state *why* it's hard in one sentence that isn't just
    "it's complicated" - a genuine constraint (e.g. "no single distributed clock", "the
    signal you'd need to fix this is exactly what privacy regulation removed", "the metric
    you can measure fastest is not the metric that matters").
(b) **Named industry solutions.** You can name at least 2-3 concrete techniques, products,
    algorithms, or papers that address it - not a category ("some companies use caching") but
    a specific instance ("Redis with TTL-based sliding windows", "Meta's ghost ads /
    Johnson-Lewis-Nubbemeyer 2017").
(c) **Real limitations.** The named solutions have honest, specific tradeoffs, not just "it
    can be expensive."

If a candidate sub-problem fails (b) or (c), you likely don't know it well enough yet to
write about it responsibly - either research it more before including it, merge it into a
neighboring sub-problem, or drop it. This filter is what keeps the output from being
plausible-sounding filler.

State the chosen sub-problems back to the user before doing the deep research pass, in one
line each - this catches a wrong domain framing early and costs nothing.

## Step 2: Parallel research

Each sub-problem is close to independent - research them in parallel rather than serially.
Use whatever parallel-execution mechanism is available in this environment, in this
preference order:

1. If the environment supports spawning separate coordinating sessions (e.g. a
   `create_session` style tool tied to a project), launch one nested session per
   sub-problem, each with a self-contained prompt (see `references/prompt-templates.md` for
   the exact template) that ends with "write your section and message back the result."
2. Otherwise, use background subagents/task-tool calls, one per sub-problem, in a single
   batch so they run concurrently, not one launched-and-awaited at a time.
3. If neither is available, research sequentially, but do not shortcut sub-problems for
   time - a rushed pass produces exactly the kind of unverified claims Step 4 exists to
   catch.

Each research pass should explicitly separate (a) why hard, (b) industry solutions with
named vendors/techniques, (c) limitations - matching the three-part test from Step 1 - and
should flag its own uncertainty rather than asserting an unfamiliar product/paper name with
false confidence. This single instruction (say "I'm not sure this name is right" instead of
inventing something plausible) is the highest-leverage line in the whole skill; models
under-do this by default.

## Step 3: Write the markdown (source of truth)

One file, ~150-250 words per sub-problem, structured as:

```markdown
# <Topic>: Deep Dive

## 1. <Sub-problem name>
**(a) Why it's hard:** ...
**(b) Industry-standard solutions:** ...
**(c) Limitations/tradeoffs:** ...

## 2. <Sub-problem name>
...
```

No generic filler paragraphs, no restating the question as the answer, no em dashes
(U+2014) - use a plain hyphen. This file is what gets edited going forward as understanding
improves; treat the HTML as a downstream artifact, not the other way around.

## Step 4: Fact-check pass (do this before building the HTML)

Domains with several similarly-named real-world products (ad platforms' lift-testing
products are a documented example: "Meta Conversion Lift" is real, "Meta's Always-On Lift"
and "Search Brand Lift" are not - the real names are different and easy to conflate) are
especially prone to a fast research pass inventing a plausible-sounding name, statistic, or
mechanism. Before treating the markdown as final:

1. Re-check every named product, paper, and statistic against what you actually know with
   confidence. If you're not sure, say so in the file rather than silently keeping the claim.
2. Prefer citing a real, checkable source (a paper name + year, a vendor's own docs page)
   over an impressive-sounding specific number you can't back up.
3. Add a short References section if the domain has citable sources (academic papers, vendor
   engineering blogs, official docs).
4. Report back exactly what you changed and why - don't silently rewrite without saying so,
   since the user may already have shared or referenced the earlier claim.

Skipping this step is the single most common way this workflow produces a wrong dashboard.
Do it even when no one asks for it explicitly.

## Step 5: Build the HTML dashboard

Full CSS/JS/HTML spec (tabs, SVG diagram helper, card layout, FAQ schema, Sync tab) is in
`references/html-dashboard-spec.md` - read it before writing the HTML, it is copy-adaptable.
In short: one self-contained file, vanilla JS, inline SVG, zero external dependencies (must
work offline via `file://`), with tabs for Overview + one per sub-problem + a vendor/
reference map + FAQ/Practice + Sync, 20-30 FAQ items with localStorage-backed progress, and
an interactive control (slider/toggle) wherever the sub-problem has real numbers to explore.

## Step 6: Register in the hub

Find or create `index.html` in the same output directory as a simple card list (see the spec
reference for the minimal hub template). Add one card linking to the new dashboard between
existing entries, matching the format already in use. If this is the first dashboard in a
directory, create the hub with just this one entry.

## Step 7: Verify (mandatory, not optional)

- Open the HTML (a local static server or an in-session JS evaluator both work) and confirm
  every tab switches, every SVG renders with no clipped/overlapping labels, and there are no
  console errors.
- Confirm the FAQ count, filters, random-question button, and mark-done checkboxes work.
- Confirm the Sync tab's export -> reset -> import round-trips progress correctly.
- Confirm the hub link resolves to the right relative path.
- Confirm zero em dashes in both the `.md` and the `.html`:
  `python3 -c "import sys;print(open(sys.argv[1]).read().count(chr(0x2014)))" <file>` must
  print `0` for each file (macOS bash 3.2 does not expand `$'\u...'`, so grepping for the
  literal character directly with grep silently checks the wrong string - use the Python
  one-liner).
- Spot-check at least one interactive control's numeric output by hand if the sub-problem
  involves a real formula (auction pricing, decay curves, statistical power) - a control that
  looks right but computes the wrong number is worse than no control.

## Output location

Ask once per project, otherwise default to `<project>/docs/<topic-slug>/` with the markdown
and HTML as `<topic-slug>.md` / `<topic-slug>.html` inside that folder, and the shared hub at
`<project>/docs/index.html`. One folder per topic keeps the markdown source of truth and its
generated HTML paired and easy to find, and keeps a prompt file (see below) alongside them.

## Reusable prompts

`references/prompt-templates.md` has copy-paste-ready prompt text for Steps 2-6 with
`{PLACEHOLDER}` slots, plus the exact fact-check prompt from Step 4. After finishing a topic,
save a filled-in copy as `<topic-slug>/PROMPT.md` next to that topic's `.md`/`.html`, so the
exact prompts used (and any corrections discovered while fact-checking) are preserved for
reapplying this workflow to the next domain.

## Sensitivity

If the domain touches employer-internal systems, names, or data, keep the output in a
private location and never place it in a public repo or public hosting without scrubbing
internal specifics first.
