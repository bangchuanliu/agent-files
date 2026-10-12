# Skill rules

Load when the document is a skill (creating, refactoring, reviewing, or auditing one). These rules add to `SKILL.md`; everything there still applies.

## Structure

- MUST build the skill from these sections. Objective, Guardrails & Constraints, and Verification are required; include the others only when the skill has something specific to say in them:
  - **Objective** - what the skill does, why, its scope, and observable success.
  - **Context & Tools** (optional) - specific tools, scripts, references, or context the skill needs, and when to use each.
  - **Guardrails & Constraints** - non-negotiable requirements, boundaries, and the policy for each runtime unknown.
  - **Preferences** - preferred approaches, not mandatory workflows.
  - **Output** - the minimum information or artifacts the caller needs; adapt format and detail to the task.
  - **Verification** - task-specific acceptance criteria, using the cheapest reliable evidence.

## Description and Objective

- MUST make the description and the Objective each clear on its own, because the agent routes on the description alone and a human decides from it and the Objective without reading further:
  - the description says in plain words what the skill does or produces, gives one trigger per distinct branch, and ends with `NOT for:` naming the nearest jobs it does not do, each routed to the skill that does it when one exists; a user-invoked skill gets a one-line human summary instead;
  - the Objective opens with one sentence a human can read alone, saying what the skill does and the outcome it delivers, followed by why and observable success;
  - the description and the body agree: every branch the description promises is handled in the body, and every branch the body handles is reachable from the description.

## Existence and overlap

- IF creating or auditing a skill, MUST confirm it earns its existence: it carries something one line in `AGENTS.md` cannot (a script, template, schema, non-default facts, a gate, or a contract another skill reads). IF one line carries it, deliver that line instead of the skill, and update every skill or doc that names it.
- IF creating or auditing a skill, MUST check the installed skills' descriptions for one covering the same triggers or output. IF one does, extend or merge into it instead of adding a parallel skill; IF two stay separate on purpose (e.g. opposite literals that must not mix), give each a `NOT for:` route to the other.
- A shared skill routes only to other shared skills; it names a private or company skill nowhere, so it works for every installer.

## Frontmatter

- `name:` required; kebab-case matching the folder.
- `kind:` required; `leaf` performs work directly, `orchestrator` routes or coordinates other skills or workers.
- `description:` required; see Description and Objective above.
- `disable-model-invocation: true` (optional) makes the skill user-invoked.
- `agents:` (optional) limits installation to matching host adapters, e.g. `agents: claude, copilot` (honoured by `lib/links.sh supports()`); absent means all. Tool-specific instructions still need a portable fallback.
- IF the target agent's skill spec differs from this repo's, MUST validate the frontmatter against the target spec.

## Invocation choice

- **Model-invoked** (no `disable-model-invocation`): the description stays loaded, so the agent and other skills can fire it, and users can still call it by name. Costs permanent context load. Use when the agent or another skill must reach it, or to host reference shared by several skills.
- **User-invoked** (`disable-model-invocation: true`): only a human can fire it; zero context load, but the human must remember it. Use when it only ever fires by hand. Reference shared by two user-invoked skills belongs in a plain file outside the skill system.

## Splitting

- IF considering a split, SHOULD check it earns its cost in _context load_ or _cognitive load_:
  - split by sequence only when later steps tempt the agent to rush the current one;
  - split off a model-invoked skill only when a distinct leading word you actually use should trigger it on its own, or another skill must reach it; the new description's context load must be worth that reach.

## Router skills

When user-invoked skills pile up past memory, add one user-invoked **router skill** that names the others and when to use each. It can only hint, never fire them.

## Checks

- `python3 scripts/spec_check.py --house <skill-dir>` (or `--all <skills-root>`) passes, run before and after editing.
- IF `scripts/spec_check.py` changes, `python3 scripts/test_spec_check.py` passes.
