## Guardrails

- Base every judgement on verified facts; label each claim verified, inferred, or assumed, and state risks and disagreement directly with the reasoning.
- Never store secret values in instructions, skills, code, commits, or messages.
- Never start anything that spawns a large swarm of subagents without explicit user approval.
- Use a plain dash "-" wherever an em dash (U+2014) would go; never emit the em dash character.

## Constraints

- When rules conflict, resolve in this order: correctness and security, then simplicity and clarity, then performance when justified by scale, then style and conventions.

## Rule index

Load every file whose trigger matches the task, and only those.

- MUST resolve `{RULE_DIR}` to an absolute path before loading any file below:

| Load when | File |
|---|---|
| brainstorming, specs, design, planning, research, or investigation | `{RULE_DIR}/thinking.md` |
| writing, reviewing, debugging, testing, committing, or releasing code or config | `{RULE_DIR}/building.md` |
| docs, readouts, status updates, messages, or review comments | `{RULE_DIR}/communicating.md` |
| an unfamiliar tool name or abbreviation, such as orca or herdr | `{RULE_DIR}/glossary.md` |
