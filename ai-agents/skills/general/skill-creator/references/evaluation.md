# Evaluation

## MUST and deletion audit

Run on every new or edited skill:

- **Each `MUST`:** name what breaks if it is dropped. Nothing concrete: demote it to `SHOULD` or an example, or delete it.
- **Each deleted line:** was it a gate (human approval, irreversible action), an invariant, or a contract another stage reads? Yes: keep it, rewritten as an outcome rule.

## Regression evaluation

Build a small representative suite (e.g., 10–20 tasks), including normal cases, edge cases, and failure modes. Compare old and new skills with the same model, codebase, tools, and task inputs where possible. Repeat nondeterministic tests.

Where no eval harness exists, run each task once with the old skill and once with the new one in isolated sub-agents (or fresh sessions), save the outputs side by side, and grade them against the metrics below.

Track:

- **Task success / correctness:** did the skill achieve the intended outcome?
- **Critical miss rate:** were serious defects or mandatory checks missed?
- **Instruction compliance:** were hard rules obeyed?
- **Evidence quality:** are claims grounded and verification honestly reported?
- **Efficiency:** tokens, latency, and unnecessary tool calls.

Do not accept lower token use as a win if correctness or safety degrades materially.
