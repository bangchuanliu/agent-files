# Evaluation

## MUST and deletion audit

Run on every new or edited skill:

- **Each `MUST`:** name what breaks if it is dropped. Nothing concrete: demote it to `SHOULD` or an example, or delete it.
- **Each deleted line:** was it a gate (human approval, irreversible action), an invariant, or a contract another stage reads? Yes: keep it, rewritten as an outcome rule.

## Regression evaluation

A rewrite is adopted only when evidence shows no material regression against the old version.

- The suite is representative: normal cases, edge cases, and failure modes, typically 10-20 tasks.
- Old and new run under the same model, codebase, tools, and task inputs, each in an isolated context (an eval harness, sub-agent, or fresh session). Nondeterministic tasks are repeated.
- Outputs are kept side by side and each pair is graded on:
  - **Task success / correctness:** did the skill achieve the intended outcome?
  - **Critical miss rate:** were serious defects or mandatory checks missed?
  - **Instruction compliance:** were hard rules obeyed?
  - **Evidence quality:** are claims grounded and verification honestly reported?
  - **Efficiency:** tokens, latency, and unnecessary tool calls.
- Lower token use counts as a win only when correctness and safety hold.
