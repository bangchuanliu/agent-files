# experimental/

Parked skills. Not installed into any agent.

`install.sh` only globs `ai-agents/skills/*/`, so anything here is invisible to Claude Code
and Copilot CLI. To reactivate a skill, move its directory back into `ai-agents/skills/` and
re-run `./install.sh`.

| Skill | Parked because |
|---|---|
| `code-simplify` | Superseded for skill files by `skill-improver`, whose simplify pass has the "Do NOT cut" guards. Its source-code simplification role overlaps `review-self`. |
