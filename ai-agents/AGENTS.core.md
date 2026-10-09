- Never use the em dash character (U+2014). Use a plain dash "-" instead.
- NEVER auto-add agent name as co-author in commit message or PR description.
- Never manually modify `CHANGELOG.md` files or any auto-generated file.
- Prefer quality, simplicity, robustness, scalability, and long-term maintainability over development cost.
- For one-off or infrequent operational work, start with the simplest direct end-to-end path. Do
  not build wrappers, control planes, policy layers, custom verifiers, or automation unless the
  direct path exposes a concrete blocker or a repeated need that justifies the added machinery.
- When fixing bugs, always start by reproducing the bug end-to-end, as close as possible to how an
  end user would experience it. This makes sure you find the real problem so your fix actually
  solves it.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel
  perfection. If something clearly looks off, even if it is unrelated to what you are doing, try to
  get it fixed along the way.
- Hold the same bar for engineering excellence: never commit broken or untested code, and fix
  lint errors, test failures, and flaky tests you encounter even when your work didn't cause them.
- Before using "dynamic workflows", "ultra code", or any harness feature that immediately spawns a
  large swarm of subagents, explain the tradeoffs and ask the user for explicit approval.
- Prioritize correctness over agreement, state risk directly and give the reasoning
  alongside the verdict.
- When rules conflict, resolve in this order: correctness and security, then simplicity and
  clarity, then performance (when justified by scale), then style and conventions.
- Always write tests; never ask whether they are wanted. Every bug fix needs a regression test.

## Machine-local configuration

Use `~/.agent/AGENTS.md.local` for private agent instructions,
`~/.agent/skills.local/` for private skills, and `~/.agent/agents.local/` for
private agents. Never commit, print, or copy their contents into tracked or
public files.

Never store secret values in agent instructions or skills. Use the approved
secret-management system instead.
