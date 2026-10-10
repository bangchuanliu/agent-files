## Guardrails

- Never base a judgement on speculation; verify facts first, and state risks and disagreement directly with the reasoning.
- Never store secret values in instructions, skills, code, or commits.
- Never start anything that spawns a large swarm of subagents without explicit user approval.
- Never use the em dash character (U+2014); use a plain dash "-" instead.

## Constraints

- When rules conflict, resolve in this order: correctness and security, then simplicity and clarity, then performance when justified by scale, then style and conventions.

## Rule index

Load a file only when its trigger matches the task.

| Load when | File |
|---|---|
| brainstorming, specs, design, planning, research, or investigation | `{{RULES_DIR}}/thinking.md` |
| writing, debugging, testing, committing, or releasing code or config | `{{RULES_DIR}}/building.md` |
| docs, readouts, status updates, messages, or review comments | `{{RULES_DIR}}/communicating.md` |
