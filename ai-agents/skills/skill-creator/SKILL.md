---
name: skill-creator
kind: leaf
description: "Use when: create, refactor, review, or tighten a document an agent consumes - a skill, a skill description, AGENTS.md, or CLAUDE.md; audit one for bloat, no-ops, unnecessary workflow, or spec conformance; evaluate a skill rewrite against the old version. NOT for: simplifying source code -> use review-self."
---

# Skill Creator

**Constraint-first, workflow-on-demand.** A document an agent consumes says what must be true, not every step to take. The agent plans; the document keeps it safe, correct, and verifiable, and steers it to the same _process_ on every run.

## Objective

Create, refactor, review, or tighten a skill, `AGENTS.md`, `CLAUDE.md`, or a doc reached through a pointer. Success means:
- the trigger is clear and the success criteria can be observed;
- every line changes behaviour;
- every pointer fires on the right branches;
- it works under any host agent;
- hard rules survive the edit;
- the spec check passes;
- for a material rewrite, evaluation shows no regression.

Terms in _italics_ are defined in [references/levers.md](references/levers.md). Load it when a term or the reasoning behind a rule is unclear, or when you need to justify a change.

## Rules

- MUST structure a skill as **Objective** (task, scope, success criteria), **Rules**, **Output & Verification**, and **Conditional Checks** when applicable. [references/template.md](references/template.md) has a template and a worked example.
- MUST write hard rules as `MUST`, defaults as `SHOULD`, and context-dependent behaviour as `IF` / `WHEN`. State the target behaviour positively (avoid _negation_). Reserve `MUST NOT` for hard guardrails that cannot be phrased positively, and pair it with the positive target.
- MUST put constraints (scope, format, allowed operations) and guardrails (secrets, unauthorized writes, fabricated evidence) together under Rules. Add a separate `Safety Guardrails` section only for high-risk work.
- MUST prescribe an ordered sequence only when skipping or reordering steps would compromise correctness, safety, recoverability, or an external protocol. Otherwise state the outcome and let the agent choose the steps.
- MUST preserve every hard requirement, safety boundary, and critical check of the original document. Edits change how reliably it is followed, not what it asks for, unless the user asks otherwise. Never drop a check just to save tokens.
- MUST keep the document agent-agnostic. Any instruction tied to one host agent's tools or features needs a portable fallback.
- MUST keep each meaning in a _single source of truth_:
  - restate nothing that global or project instructions already say;
  - remove _duplication_;
  - leave the _environment_ (config, scripts, `--help`, directory layout) to speak for itself, unless the lookup is expensive or the fact is unwritten.
- MUST delete _no-ops_ (sentences that change nothing compared with the model's default) as whole sentences. Also delete lines that have lost _relevance_. Settle a disputed no-op by running the document, not by arguing.
- SHOULD place material on the _information hierarchy_ by branch:
  - inline what every branch needs, including every essential rule;
  - disclose branch-only detail behind a _context pointer_ in `references/`, and say when to load it;
  - put deterministic checks in `scripts/`;
  - _co-locate_ a concept's definition, rules, and caveats.
- SHOULD make domain checks conditional on context, not one long checklist every time. Treat _sprawl_ as a defect.
- SHOULD collapse a repeated phrase or triad into a _leading word_, preferring one the model already knows from pretraining.

## Conditional Checks

- IF the document is a skill, read [references/skill-mechanics.md](references/skill-mechanics.md) (frontmatter, invocation choice, router skills). Run `python3 scripts/spec_check.py --house <skill-dir>` (or `--all <skills-root>`) before and after editing.
- IF editing a _context pointer_ (a skill description, or an `AGENTS.md` line that names a doc):
  - put the leading word first;
  - give one trigger per distinct branch, collapsing synonyms;
  - cut any identity the body already carries;
  - add `NOT for:` routing when another skill covers the same triggers.

  Sharpen a weak pointer before inlining the material it points to.
- IF the document has steps, each step MUST end on a checkable _completion criterion_. To counter _premature completion_, sharpen the criterion first. Split the sequence only if the rush is observed, and only across a real context boundary.
- IF considering a split, check it earns its cost in _context load_ or _cognitive load_:
  - split by sequence only when later steps tempt the agent to rush the current one;
  - split by invocation per [references/skill-mechanics.md](references/skill-mechanics.md).
- IF refactoring or materially changing an existing document, list its branches and hard rules first. Then evaluate the new version against the old before adopting it, per [references/evaluation.md](references/evaluation.md).
- IF the target agent's skill spec differs from this repo's, validate the frontmatter against the target spec.
- IF `scripts/spec_check.py` changes, run `python3 scripts/test_spec_check.py`.

## Output & Verification

- **Create or refactor:** deliver the files, the spec-check result from before and after, and the evaluation result, or a statement of why evaluation was not run.
- **Review or audit:** for each item, report pass, fail, or partial with line-level evidence, the lever it concerns (no-op, duplication, negation, weak pointer, sprawl, unnecessary workflow), and a fix. Say plainly if nothing needs changing.
- Confirm that every original branch and hard rule survived. List anything removed and why.
- Distinguish verified facts from judgement calls, such as no-ops judged rather than tested. State any check that could not be completed.

**Review checklist:**
- clear trigger, scope, and objective;
- observable success criteria;
- hard rules distinct from preferences;
- no redundant global instructions;
- no unnecessary fixed workflow, and mandatory order preserved;
- context-specific checks are conditional;
- concise output requirements;
- explicit verification and uncertainty reporting;
- references available on demand;
- no material regression on evaluation.

**Decision rule:** keep a directive if removing it materially increases the chance of failure, unacceptable behaviour, or an unverifiable result. Otherwise simplify it, make it conditional, move it out, or remove it.
