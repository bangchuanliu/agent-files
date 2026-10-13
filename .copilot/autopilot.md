---
applyTo: "**"
---

# Autopilot mode rules

Apply these rules only while Copilot CLI autopilot mode is active. Outside autopilot, ignore this file.

## Completing a task

- The `task_complete` summary is the only message the user is guaranteed to read, so write it for someone who was not watching the session.
- Always include a customer-facing summary in the `task_complete` summary, covering:
  - **Outcome**: what was delivered or answered, in one or two sentences of plain language.
  - **Changes**: the files, PRs, docs, or other artifacts created or modified, with links or paths.
  - **Verification**: how the result was checked (tests, builds, queries, manual reproduction) and the result.
  - **Assumptions**: any decision made on the user's behalf in place of asking.
  - **Open items**: anything left undone, blocked, or risky, and the next step the user should take; write "None" when there are none.
- Lead with the outcome, avoid internal tool names and process narration, and keep it short enough to skim.
