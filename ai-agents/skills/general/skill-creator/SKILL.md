---
name: skill-creator
kind: leaf
description: "Use when: create, refactor, review, or tighten a document an agent consumes - a skill, a skill description, AGENTS.md, or CLAUDE.md; audit one for bloat, no-ops, unnecessary workflow, or spec conformance; decide whether a skill is needed at all or should merge into another; evaluate a skill rewrite against the old version. NOT for: simplifying source code."
---

# Skill Creator

## Objective

Create, refactor, review, or tighten a skill, `AGENTS.md`, `CLAUDE.md`, or a doc reached through a pointer, so that it steers the agent by intent and guardrails rather than scripted steps. The document states what must be true - the outcome and why, the boundaries, the policy for each unknown, and how success is checked - and leaves planning to the agent, because fixed steps break on cases the author did not foresee while intent and guardrails generalize.

Success, for every document touched:

- its trigger fires on the right branches and only those;
- every hard rule traces to the user, the original document, or a listed assumption, and none of the original's was lost;
- every runtime unknown has a policy and every reachable risk has a guardrail;
- every line changes behaviour, and it works under any host agent;
- the Verification section below passes.

## Context & Tools

Load each file when its condition holds; several can apply at once (e.g. refactoring a skill loads `skills.md` and `refactor.md`).

| File | Load when | Covers |
|---|---|---|
| [references/skills.md](references/skills.md) | the document is a skill | required sections, description and Objective clarity, existence and overlap, frontmatter, invocation, splitting, spec checks |
| [references/refactor.md](references/refactor.md) | changing an existing document | baseline of branches and hard rules, converting steps, adoption gate |
| [references/review.md](references/review.md) | reviewing or auditing, and before declaring any edit done | review output and levers, the acceptance checklist |
| [references/evaluation.md](references/evaluation.md) | creating or editing a skill, or `refactor.md` sends you | the `MUST` and deletion audit, regression evaluation |
| [references/template.md](references/template.md) | writing a new skill | skeleton and a worked example |
| [references/levers.md](references/levers.md) | a term in _italics_ or the reason behind a rule is unclear | definitions and rationale |

`scripts/spec_check.py` checks skill spec conformance deterministically; `scripts/test_spec_check.py` tests it.

## Guardrails & Constraints

These hold for every document, whatever the branch.

- MUST load every reference file whose condition in the table above holds before writing or judging.
- MUST include only necessary fields and clarifications: a line belongs only if the agent would do worse without it. Leave everything else to the agent's own judgement and capabilities.
- MUST write hard rules as `MUST`, defaults as `SHOULD`, and context-dependent behaviour as `IF` / `WHEN`, each in the section its strength belongs to. State the target behaviour positively (avoid _negation_). Reserve `MUST NOT` for hard guardrails that cannot be phrased positively, and pair it with the positive target.
- MUST make every `MUST` protect correctness, safety, a contract another stage reads, or a human gate (approval, irreversible action). Demote a `MUST` that only fixes a choice the agent could make well (layout, chart type, tool, wording, step order) to `SHOULD` or an example, or delete it. A `MUST` sets a floor, never a ceiling.
- MUST capture the _intent_: the Objective's why, and one clause on each hard rule whose reason is not obvious, so the agent can apply the rule to cases the document did not anticipate.
- MUST resolve, before writing, the intent, triggers and `NOT for:` boundaries, hard rules, inputs, risky actions, and observable success. Settle each from the user's request, the existing document, or the environment. IF one stays unknown, ask the user; WHEN the user is unavailable, adopt the safest reasonable default and list it as an assumption in the output. Every hard rule and boundary in the result traces to the user, the original document, or a listed assumption.
- MUST settle every runtime question that can be settled while writing. Every remaining _runtime unknown_ (missing input, ambiguous target, missing access, failed check) gets an explicit policy: ask, proceed on a stated default, or stop and report. IF the affected action is irreversible, destructive, or writes to a shared or external system, the policy MUST be ask or stop.
- MUST give each risk the document's actions can reach a guardrail: scope, destructive or irreversible operations, writes to shared or external systems and the approval they need, secrets and personal data, fabricated evidence or results, and cost or blast radius. A risk it cannot reach needs no line.
- MUST prescribe an ordered sequence only when skipping or reordering steps would compromise correctness, safety, recoverability, or an external protocol. Otherwise state the outcome and let the agent choose the steps. IF the document keeps steps, each MUST end on a checkable _completion criterion_; to counter _premature completion_, sharpen the criterion first, and split the sequence only if the rush is observed, and only across a real context boundary.
- MUST specify an artifact for a human (report, page, readout) by what the reader must be able to answer or decide, plus a quality bar. IF a layout helps, give it as a labelled default the agent may replace.
- MUST mark an example list as non-exhaustive ("e.g. ..., or better") unless it is a closed set the agent must choose from (statuses, enum values).
- MUST preserve every hard requirement, safety boundary, and critical check of an original document. Never drop a check just to save tokens.
- MUST keep the document agent-agnostic. Any instruction tied to one host agent's tools or features needs a portable fallback.
- MUST keep each meaning in a _single source of truth_:
  - restate nothing that global or project instructions already say;
  - remove _duplication_;
  - leave the _environment_ (config, scripts, `--help`, directory layout) to speak for itself, unless the lookup is expensive or the fact is unwritten.
- MUST delete _no-ops_ (sentences that change nothing compared with the model's default) as whole sentences. Also delete lines that have lost _relevance_. A disputed no-op is settled only by evidence from running the document.

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
  - collapse synonyms that name the same branch;
  - cut filler that names the document rather than its job ("This skill is a tool that...").

  Sharpen a weak pointer before inlining the material it points to.

## Output

- **Create or refactor:** the files, every assumption adopted in place of a user answer, and what the loaded reference files add.
- **Review or audit:** as [references/review.md](references/review.md) specifies.
- Distinguish verified facts from judgement calls, such as no-ops judged rather than tested. State any check that could not be completed.

## Verification

- Every check in each loaded reference file passes (spec check for a skill, refactor baseline and audit for a change).
- The document passes the checklist in [references/review.md](references/review.md).

**Decision rule:** keep a directive, or a whole skill, if removing it materially increases the chance of failure, unacceptable behaviour, or an unverifiable result. Otherwise simplify it, make it conditional, move it out, merge it, or remove it.
