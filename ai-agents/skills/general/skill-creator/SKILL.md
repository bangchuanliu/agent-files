---
name: skill-creator
kind: leaf
description: "Use when: create, refactor, review, or tighten a document an agent consumes - a skill, a skill description, AGENTS.md, or CLAUDE.md; audit one for bloat, no-ops, unnecessary workflow, or spec conformance; evaluate a skill rewrite against the old version. NOT for: simplifying source code."
---

# Skill Creator

## Objective

Create, refactor, review, or tighten a skill, `AGENTS.md`, `CLAUDE.md`, or a doc reached through a pointer, so that its trigger is clear, every line changes behaviour, every pointer fires on the right branches, and it works under any host agent.

## Context & Tools

- [references/levers.md](references/levers.md) defines the terms in _italics_. Load it when a term or the reasoning behind a rule is unclear, or when you need to justify a change.
- [references/template.md](references/template.md) has the skill template and a worked example.
- [references/skill-mechanics.md](references/skill-mechanics.md) covers frontmatter, invocation choice, and router skills.
- [references/evaluation.md](references/evaluation.md) has the `MUST` and deletion audit, run on every new or edited skill, and covers evaluating a rewrite against the old version.
- `scripts/spec_check.py` checks skill spec conformance deterministically; `scripts/test_spec_check.py` tests it.

## Guardrails & Constraints

- MUST structure a skill from the sections below, including a section only when the skill has something specific to say in it:
  - **Objective** - what the skill accomplishes, its scope, and observable success.
  - **Context & Tools** (optional) - specific tools, scripts, references, or context the skill needs, and when to use each.
  - **Guardrails & Constraints** - non-negotiable requirements and boundaries (scope, format, allowed operations, secrets, unauthorized writes, fabricated evidence).
  - **Preferences** - preferred approaches, not mandatory workflows.
  - **Output** - the minimum information or artifacts the caller needs; adapt format and detail to the task.
  - **Verification** - task-specific acceptance criteria, using the cheapest reliable evidence.
- MUST include only necessary fields and clarifications: a line belongs only if the agent would do worse without it. Leave everything else to the agent's own judgement and capabilities.
- MUST write hard rules as `MUST`, defaults as `SHOULD`, and context-dependent behaviour as `IF` / `WHEN`, each in the section its strength belongs to. State the target behaviour positively (avoid _negation_). Reserve `MUST NOT` for hard guardrails that cannot be phrased positively, and pair it with the positive target.
- MUST make every `MUST` protect correctness, safety, a contract another stage reads, or a human gate (approval, irreversible action). Demote a `MUST` that only fixes a choice the agent could make well (layout, chart type, tool, wording, step order) to `SHOULD` or an example, or delete it. A `MUST` sets a floor, never a ceiling.
- MUST specify an artifact for a human (report, page, readout) by what the reader must be able to answer or decide, plus a quality bar. IF a layout helps, give it as a labelled default the agent may replace.
- MUST mark an example list as non-exhaustive ("e.g. ..., or better") unless it is a closed set the agent must choose from (statuses, enum values).
- MUST prescribe an ordered sequence only when skipping or reordering steps would compromise correctness, safety, recoverability, or an external protocol. Otherwise state the outcome and let the agent choose the steps.
- IF the document has steps, each step MUST end on a checkable _completion criterion_. To counter _premature completion_, sharpen the criterion first. Split the sequence only if the rush is observed, and only across a real context boundary.
- MUST settle runtime questions while writing the skill.
- MUST preserve every hard requirement, safety boundary, and critical check of the original document. Edits change how reliably it is followed, not what it asks for, unless the user asks otherwise. Never drop a check just to save tokens.
- IF refactoring or materially changing an existing document, MUST list its branches and hard rules first, then evaluate the new version against the old before adopting it, per [references/evaluation.md](references/evaluation.md).
- MUST keep the document agent-agnostic. Any instruction tied to one host agent's tools or features needs a portable fallback.
- MUST keep each meaning in a _single source of truth_:
  - restate nothing that global or project instructions already say;
  - remove _duplication_;
  - leave the _environment_ (config, scripts, `--help`, directory layout) to speak for itself, unless the lookup is expensive or the fact is unwritten.
- MUST delete _no-ops_ (sentences that change nothing compared with the model's default) as whole sentences. Also delete lines that have lost _relevance_. Settle a disputed no-op by running the document, not by arguing.
- IF the document is a skill, MUST read [references/skill-mechanics.md](references/skill-mechanics.md).
- IF the target agent's skill spec differs from this repo's, MUST validate the frontmatter against the target spec.

## Preferences

- SHOULD place material on the _information hierarchy_ by branch:
  - inline what every branch needs, including every essential rule;
  - disclose branch-only detail behind a _context pointer_ in `references/`, and say when to load it;
  - put deterministic checks in `scripts/`;
  - _co-locate_ a concept's definition, rules, and caveats.
- SHOULD make domain checks conditional on context (`IF` lines in the section matching their strength), not one long checklist every time. Treat _sprawl_ as a defect.
- SHOULD collapse a repeated phrase or triad into a _leading word_, preferring one the model already knows from pretraining.
- IF editing a _context pointer_ (a skill description, or an `AGENTS.md` line that names a doc), SHOULD:
  - put the leading word first;
  - give one trigger per distinct branch, collapsing synonyms;
  - cut any identity the body already carries;
  - add `NOT for:` routing when another skill covers the same triggers.

  Sharpen a weak pointer before inlining the material it points to.
- IF considering a split, SHOULD check it earns its cost in _context load_ or _cognitive load_:
  - split by sequence only when later steps tempt the agent to rush the current one;
  - split by invocation per [references/skill-mechanics.md](references/skill-mechanics.md).

## Output

- **Create or refactor:** the files, the spec-check result from before and after, and the evaluation result or why evaluation was not run. List anything removed and why.
- **Review or audit:** for each item, pass, fail, or partial with line-level evidence, the lever it concerns (no-op, duplication, negation, weak pointer, sprawl, unnecessary workflow), and a fix. Say plainly if nothing needs changing.
- Distinguish verified facts from judgement calls, such as no-ops judged rather than tested. State any check that could not be completed.

## Verification

- IF the document is a skill, `python3 scripts/spec_check.py --house <skill-dir>` (or `--all <skills-root>`) passes, run before and after editing.
- IF `scripts/spec_check.py` changes, `python3 scripts/test_spec_check.py` passes.
- Every original branch and hard rule survived, and the `MUST` and deletion audit in [references/evaluation.md](references/evaluation.md) passes; for a material rewrite, evaluation shows no regression.
- The document passes the review checklist:
  - clear trigger, scope, and objective;
  - only necessary sections, fields, and clarifications;
  - observable success criteria;
  - hard rules distinct from preferences;
  - no redundant global instructions;
  - no unnecessary fixed workflow, and mandatory order preserved;
  - context-specific checks are conditional;
  - concise output requirements;
  - explicit verification and uncertainty reporting;
  - references available on demand.

**Decision rule:** keep a directive if removing it materially increases the chance of failure, unacceptable behaviour, or an unverifiable result. Otherwise simplify it, make it conditional, move it out, or remove it.
