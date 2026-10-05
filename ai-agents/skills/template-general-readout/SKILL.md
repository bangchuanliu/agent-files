---
name: template-general-readout
kind: leaf
description: "Readout structure: emit a genre skeleton or restructure an existing readout without changing its content. Genres: data validation (technical, leadership, one-pager), strategy, launch, research, program, postmortem. Use for readout templates, section selection, or reformatting. NOT for: domain methodology, RCA narratives (template-doc-data-issue-rc), or executing validation."
---

# General Readout Template

A readout is a document that ends in a **decision or an ask**, backed by evidence. This skill
owns **structure only**: which sections exist, in what order, and what goes in each. It carries
no domain methodology. A domain-specific skill in a company or local layer may call this skill
for the skeleton and own its own content rules; this skill never calls domain skills.

## Interface

| Argument | Values | Default |
|---|---|---|
| `mode` | `skeleton` · `restructure` | `skeleton` |
| `genre` | `data-validation` · `strategy` · `launch` · `research` · `program` · `postmortem` | infer |
| `variant` | `technical` · `leadership` · `onepager` (data-validation only) | `technical` |
| `source` | existing readout (Google Doc / Markdown) - `restructure` only | none |

Infer from the request and state what you inferred. If two genres fit, pick by the **ask**, not
the content.

## Genres

| Genre | The question it answers | Skeleton |
|---|---|---|
| **Data validation / migration** | Do the new numbers match, and can we ship them? | `genres/data-validation/{technical,leadership,onepager}.md` |
| **Strategy / exploration** | Is this area healthy; what do we start, stop or continue? | `genres/strategy.md` |
| **Launch / staged rollout / GA** | Did this stage meet its criteria, and do we advance? | `genres/launch.md` |
| **Qualitative research** | What did customers tell us; is the concept validated? | `genres/research.md` |
| **Program / portfolio review** | Across N workstreams, where do we invest? | `genres/program.md` |
| **Incident / postmortem** | What broke, what did it cost, what prevents recurrence? | `genres/postmortem.md` |

The data-validation genre is self-contained: its three files are full skeletons with their own
numbered sections. The other genres add sections to the universal spine below.

**Section numbers are a contract.** Domain or local skills may cite them (for example,
data-validation §3a, §5a, Appendix B). Never renumber a skeleton without updating every
skill that references it.

## Universal spine (non-data-validation genres)

Every genre carries these. Order may vary; presence may not.

1. **Header** - author, date, status (draft/final), scope and period, link to evidence.
2. **TL;DR** - the answer and the ask, written last, placed first.
3. **The ask** - decision, owner, date, recommendation, confidence and what limits it.
4. **Evidence and method** - what you looked at, how, and the population or sample.
5. **Findings** - only those that can change the decision. Each with a ✅ established /
   ⚠️ not yet proven verdict.
6. **Recommendation** - with alternatives considered.
7. **Next steps** - work, owner, priority, effort, timeline.
8. **What this does not tell you** - the limits of the claim. Never optional.
9. **Appendix** - detail, references, glossary if the audience needs it.

## Mode: skeleton

1. Pick genre (and variant for data validation); read only that skeleton file.
2. Emit it with placeholders intact. Drop a section only if it cannot change the decision, and
   say which you dropped.
3. Output as a native Google Doc (never uploaded `.docx`) or repo Markdown, as requested.

## Mode: restructure

Move content; never rewrite it.

1. Read the source in full, then pick the genre by its ask.
2. Map every source block to a target section. Keep text, numbers, tables and links
   **verbatim** - no new numbers, no softened caveats, no changed conclusions.
3. Produce the restructured document plus three lists:
   - **Mapping** - source heading → target section.
   - **Missing** - required target sections with no source content, left as placeholders.
   - **Unplaced** - source content that fits no section, kept in an appendix, never dropped.
4. Never modify the source doc; write a new doc or file.

Restructuring fixes shape only. Whether the content is *correct* is the domain skill's review.

## Audience

Produce a technical version for the owning team; derive a leadership version when the decision
leaves the team. **Derive, never author leadership first**: no new numbers, values and status
match, simplify language never the conclusion. Data validation spells out the extraction in
`genres/data-validation/leadership.md`.

## Craft rules

- Write the TL;DR last; lead with the answer, not the journey.
- Every number has a source; every estimate names its benchmark.
- Say whether a number is good, not only what it is - anchor to a prior period or peer.
- Keep *demonstrated* and *suspected* apart, in every section.
- Include a section only if it changes the decision. Empty scaffolding is noise.
