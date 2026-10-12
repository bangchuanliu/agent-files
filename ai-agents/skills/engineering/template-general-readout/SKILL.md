---
name: template-general-readout
kind: leaf
description: "Use when: producing the structure of a readout (a document that ends in a decision or ask) - emit a genre skeleton, restructure an existing readout without changing its content, or derive a leadership version or one-pager from a technical one. Genres: data validation (technical, leadership, one-pager), strategy, launch/GA, research, program review, postmortem. NOT for: domain methodology or checking the content is correct, data-incident RCA narratives, running a validation, or HTML review pages (html-report)."
---

# General Readout Template

## Objective

Give a readout the right structure for its genre - which sections exist, in what order, and what goes in each - either as an empty skeleton or by moving an existing readout's content into that structure unchanged. A readout is a document that ends in a **decision or an ask**, backed by evidence; a consistent structure lets the reader find the ask, the evidence, and the limits of the claim quickly.

This skill owns **structure only** and carries no domain methodology. A domain-specific skill in a company or local layer may call it for the skeleton and own its content rules; this skill never calls domain skills.

Success: the output follows the chosen genre's skeleton, keeps every required section, states what was inferred or dropped, and (when restructuring) carries every piece of source content verbatim.

## Context & Tools

Pick the genre by the question the readout answers, then read only its skeleton file:

| Genre | The question it answers | Skeleton |
|---|---|---|
| **Data validation / migration** | Do the new numbers match, and can we ship them? | `genres/data-validation/{technical,leadership,onepager}.md` |
| **Strategy / exploration** | Is this area healthy; what do we start, stop or continue? | `genres/strategy.md` |
| **Launch / staged rollout / GA** | Did this stage meet its criteria, and do we advance? | `genres/launch.md` |
| **Qualitative research** | What did customers tell us; is the concept validated? | `genres/research.md` |
| **Program / portfolio review** | Across N workstreams, where do we invest? | `genres/program.md` |
| **Incident / postmortem** | What broke, what did it cost, what prevents recurrence? | `genres/postmortem.md` |

The data-validation genre is self-contained: its three files are full skeletons with their own numbered sections. The other genres add sections to the universal spine below.

Inputs, inferred from the request when not given:

| Argument | Values | Default |
|---|---|---|
| `mode` | `skeleton` · `restructure` | `skeleton` |
| `genre` | `data-validation` · `strategy` · `launch` · `research` · `program` · `postmortem` | infer |
| `variant` | `technical` · `leadership` · `onepager` (data-validation only) | `technical` |
| `source` | existing readout (Google Doc / Markdown) - `restructure` only | none |

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

## Guardrails & Constraints

- MUST keep every skeleton's section numbers unchanged, because domain or local skills cite them (for example data-validation §3a, §5a, Appendix B). Renumbering is allowed only together with updating every skill that references them.
- MUST state the inferred `mode`, `genre`, and `variant`. IF two genres fit, pick by the **ask**, not the content.
- MUST keep "What this does not tell you" (or the data-validation equivalent) in every output.
- IF `mode` is `skeleton`, MUST emit the chosen skeleton with placeholders intact. Drop a section only if it cannot change the decision, and name each dropped section.
- IF `mode` is `restructure`:
  - MUST read the source in full before choosing the genre, and pick it by the source's ask;
  - MUST move content, never rewrite it: text, numbers, tables, and links stay **verbatim** - no new numbers, no softened caveats, no changed conclusions;
  - MUST map every source block to a target section; content that fits no section goes to an appendix, never dropped;
  - MUST leave the source untouched and write the result to a new doc or file;
  - MUST report three lists: **Mapping** (source heading -> target section), **Missing** (required target sections with no source content, left as placeholders), **Unplaced** (source content kept in the appendix).
- IF producing a leadership version or one-pager, MUST derive it from a completed technical readout, never author it first: no new numbers, values and status match the technical readout, simplify the language but never the conclusion. Data validation spells out the extraction in `genres/data-validation/leadership.md` and `onepager.md`. IF no technical readout exists, MUST ask whether to start from the technical skeleton.
- IF the output is a Google Doc, MUST create it as a native Google Doc, not an uploaded `.docx`. IF the user named no format, SHOULD produce repo Markdown and say so.
- IF the source cannot be read in full, MUST stop and report rather than restructure a partial document.

## Preferences

- SHOULD produce the technical version for the owning team, and derive a leadership version when the decision leaves the team.
- SHOULD give every number a source and every estimate its benchmark, and say whether a number is good by anchoring it to a prior period or peer.
- SHOULD include a section only if it can change the decision; empty scaffolding is noise.

## Output

- The skeleton or restructured document (or a link to it), plus the inferred arguments and any dropped sections.
- For `restructure`: the Mapping, Missing, and Unplaced lists.

## Verification

- The output's section numbers and headings match the chosen skeleton file.
- For `restructure`: every source block appears in Mapping or Unplaced, and a spot check of numbers and caveats against the source shows them unchanged. Whether the content is *correct* is the domain skill's review, not this one.
- For a leadership version or one-pager: every figure and status matches the technical readout.
