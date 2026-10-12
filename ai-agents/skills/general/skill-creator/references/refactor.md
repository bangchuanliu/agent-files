# Refactor rules

Load when refactoring, tightening, or materially changing an existing document. These rules add to `SKILL.md`; everything there still applies.

- MUST list the original's branches and hard rules before editing; that list is the baseline every later check compares against.
- MUST convert each step of the original into the outcome, guardrail, or verification check it protects, keeping it as a step only under `SKILL.md`'s sequence rule. A step that protects nothing is removed and listed.
- MUST run the `MUST` and deletion audit in [evaluation.md](evaluation.md), and for a material rewrite, its regression evaluation, before adopting the new version.
- Edits change how reliably the document is followed, not what it asks for, unless the user asks otherwise.

## Output additions

- The spec-check result from before and after (for a skill), and the evaluation result or why evaluation was not run.
- Anything removed and why.
