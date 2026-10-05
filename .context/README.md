# Local context

Create `context.md` in this directory after cloning this repository and record the instructions
for the company, client, project, or other working context.

`context.md` is deliberately ignored by Git and is **not** installed into Claude Code, Copilot
CLI, or Pi global instructions. This prevents one checkout's company-specific information from
leaking into every project handled by those agents.

Use this file as local reference material while working in this checkout. Put instructions that
must affect a particular codebase in that codebase's own agent instruction file instead.
