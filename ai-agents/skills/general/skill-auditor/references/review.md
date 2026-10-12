# Review rules

Load when reviewing or auditing a document, and before declaring any created or edited document done (the checklist is the acceptance bar for every branch).

## Review output

- For each item: pass, fail, or partial with line-level evidence, the lever it concerns, and a fix. Say plainly if nothing needs changing.
- Levers: unneeded skill, duplicate skill, unclear description or objective, description-body mismatch, missing intent, unhandled unknown, uncovered risk, no-op, duplication, negation, weak pointer, sprawl, unnecessary workflow.
- A review edits nothing unless the user asks for fixes.

## Checklist

- the skill earns its existence and no installed skill already covers it;
- description and Objective each clear on their own (what it does, triggers, `NOT for:`, why, success) and in agreement with the body;
- every runtime unknown has an ask, default, or stop policy;
- every reachable risk has a guardrail;
- every hard rule traces to the user, the original, or a listed assumption;
- only necessary sections, fields, and clarifications;
- observable success criteria;
- hard rules distinct from preferences;
- no redundant global instructions;
- no unnecessary fixed workflow, and mandatory order preserved;
- context-specific checks are conditional;
- concise output requirements;
- explicit verification and uncertainty reporting;
- references available on demand.

The first two items apply only to skills.
