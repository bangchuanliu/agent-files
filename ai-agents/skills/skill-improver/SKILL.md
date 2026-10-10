---
name: skill-improver
kind: leaf
description: "Use when: improve the wording, pointers, or information hierarchy of a document an agent consumes - a skill, a skill description, AGENTS.md, or CLAUDE.md; audit one for bloat, no-ops, or spec conformance. NOT for: creating a skill or restructuring one into rules and conditional checks -> use skill-creator; simplifying source code -> use review-self."
---

# Skill Improver

## Objective

Improve any document an agent consumes (a skill, `AGENTS.md`, `CLAUDE.md`, or a doc reached through a pointer) so the agent follows the same _process_ on every run. Success means four things:
- every line changes the agent's behaviour;
- every pointer fires on the right branches;
- the document works under any host agent;
- the document still asks for what it asked for before.

Terms in _italics_ are defined, with their reasoning, in [references/levers.md](references/levers.md). Load it when a term or the reason behind a rule is unclear, or when you need to justify a change.

## Rules

- MUST keep the document agent-agnostic. Any instruction that depends on one host agent's tools or features needs a portable fallback.
- MUST preserve the document's intended behaviour and hard rules. Edits change how reliably the document is followed, not what it asks for, unless the user asks otherwise.
- MUST keep each meaning in a _single source of truth_. Remove _duplication_. Do not restate the _environment_ (config, scripts, `--help`, directory layout) unless the lookup is expensive or the fact is unwritten: a convention, a reason, or a gotcha.
- MUST delete _no-ops_ (sentences that change nothing compared with the model's default) as whole sentences. When a no-op is disputed, settle it by running the document, not by arguing.
- MUST prune lines that have lost _relevance_: pure exposition, stale facts, and branches that belong behind a pointer.
- SHOULD state the target behaviour positively (avoid _negation_). Keep a prohibition only as a hard guardrail that cannot be phrased positively, and pair it with the positive target.
- SHOULD collapse a repeated phrase or triad into a _leading word_. Prefer a word the model already knows from pretraining over a coined one. Replace a word too weak to beat the default with a stronger one.
- SHOULD place material on the _information hierarchy_ by branch. Inline what every branch needs. Disclose behind a _context pointer_ what only some branches reach. _Co-locate_ a concept's definition, rules, and caveats under one heading.
- SHOULD treat _sprawl_ as a defect even when every line is live. The fix is to disclose or split.

## Conditional Checks

- IF the document is a skill, read [references/skill-mechanics.md](references/skill-mechanics.md) (frontmatter, invocation choice, router skills). Run `python3 scripts/spec_check.py <skill-dir>` (or `--all <skills-root>`) before and after editing.
- IF editing a _context pointer_ (a skill description, or an `AGENTS.md` line that names a doc):
  - put the leading word first;
  - give one trigger per distinct branch, collapsing synonyms;
  - cut any identity the body already carries.
  
  Sharpen a weakly worded pointer before inlining the material it points to.
- IF the document has steps, each step MUST end on a _completion criterion_ the agent can check, and that criterion should be demanding enough to force the legwork. Against _premature completion_, sharpen the criterion first. Split the sequence to hide later steps only if the rush is actually observed, and only across a real context boundary such as a hand-off or a subagent.
- IF considering a split, check it earns its cost in _context load_ or _cognitive load_:
  - split by sequence only when later steps tempt the agent to rush the current one;
  - split by invocation per [references/skill-mechanics.md](references/skill-mechanics.md).
- IF `scripts/spec_check.py` changes, run `python3 scripts/test_spec_check.py`.

## Output & Verification

- For an edit, deliver the edited document. For an audit, list findings, each with its line, the lever it concerns (for example no-op, duplication, negation, weak pointer, sprawl), and a fix.
- For a skill, report the spec-check result from before and after the edit.
- Confirm the edited document still covers every branch and hard rule of the original. List anything removed and why.
- State what was not verified, for example no-op calls that were judged rather than tested by running the document.
