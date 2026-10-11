# Skill mechanics

What changes when the document is a skill. Everything else is in `SKILL.md` and `levers.md`.

## Frontmatter

- `name:` required; kebab-case matching the folder.
- `kind:` required; `leaf` performs work directly, `orchestrator` routes or coordinates other skills or workers.
- `description:` required; model-facing context pointer for model-invoked skills, one-line human summary for user-invoked ones.
- `disable-model-invocation: true` (optional) makes the skill user-invoked.
- `agents:` (optional) limits installation to matching host adapters, e.g. `agents: claude, copilot` (honoured by `lib/links.sh supports()`); absent means all. Tool-specific instructions still need a portable fallback.

## Invocation choice

- **Model-invoked** (no `disable-model-invocation`): the description stays loaded, so the agent and other skills can fire it, and users can still call it by name. Costs permanent context load. Use when the agent or another skill must reach it, or to host reference shared by several skills.
- **User-invoked** (`disable-model-invocation: true`): only a human can fire it; zero context load, but the human must remember it. Use when it only ever fires by hand. Reference shared by two user-invoked skills belongs in a plain file outside the skill system.

## Splitting by invocation

Split off a model-invoked skill only when a distinct leading word you actually use should trigger it on its own, or another skill must reach it; the new description's context load must be worth that reach.

## Router skills

When user-invoked skills pile up past memory, add one user-invoked **router skill** that names the others and when to use each. It can only hint, never fire them.
