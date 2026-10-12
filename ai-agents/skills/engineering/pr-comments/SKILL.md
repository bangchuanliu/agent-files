---
name: pr-comments
kind: leaf
description: "Use when: addressing feedback on my PR - review comments, reviewer questions, failing CI checks, merge conflicts (address / respond to / fix PR comments); watching my PR until it is approved - babysit, shepherd, poll a PR, 'post PR'. NOT for: reviewing someone else's PR (review-others), or creating or updating a PR from local changes."
---

# PR Comments

## Objective

Move a PR toward approval: every review thread, PR comment, review body, failing check, and merge conflict the watcher surfaces is fixed, answered, handed to the user, or returned to the caller. By default this is one pass. A watch keeps going until the PR is approved, merged, or closed, or the watcher stops it.

## Context & Tools

- `scripts/pr_watch.py` (see `--help`) polls the PR through `gh` with no model tokens between polls: `status` takes one snapshot, `wait` blocks until something is actionable, and `mark` records handled item keys. Its JSON output defines the statuses and item fields. State persists per PR, so a relaunched run resumes where the last one stopped.
- Replies go through `gh`: a thread reply targets the item's `reply_to_comment_id` (`gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body=...`); a PR-level reply uses `gh pr comment`.
- Read `~/.agents-local/rules/skill-context/pr-comments/context.md` if it exists; it may name the repo's commit workflow or an orchestrator that owns some PRs. Its absence is normal.
- **Modes:**
  - **fix** (default): this agent changes the code, commits, pushes, and replies.
  - **triage** (the caller says it owns code changes, e.g. an orchestrator running other stages in the same checkout): this agent replies and returns all code work to the caller.

  Either mode runs one `status` pass, or loops on `wait` when asked to watch, babysit, or shepherd the PR, or when launched in triage by an orchestrator.

## Guardrails & Constraints

- MUST sort every surfaced item into exactly one of:
  - **reply:** a question, a request for explanation, or a point the code already handles.
  - **code fix:** anything that needs a code, test, or config change, including a failing check caused by the change and a merge conflict.
  - **user:** a judgment call (design disagreement, scope expansion, product decision, a second pushback on the same point) or a failure needing access or approval.
- MUST verify a bot reviewer's (`is_bot`) claim before calling it a code fix.
- MUST write replies only as the user would stand behind them; they are posted as the user.
- MUST leave merging, approving, dismissing reviews, closing the PR, and resolving threads to humans; addressed threads stay open for the reviewer.
- MUST rerun a flaky or infrastructure check failure at most once (`gh run rerun <run_id> --failed`), then treat it as a code fix or user item.
- MUST `mark` every item once it is dealt with, including items not acted on, because unmarked items resurface on the next poll. Mark with `--pushed` only items fixed by a push.
- MUST keep the script's `--max-rounds` default; reaching it means fixes are not converging.
- IF `wait` returns `idle`, MUST call `wait` again. IF the script returns `stop` or `error`, MUST stop and report.
- IF in fix mode:
  - MUST work in a checkout of the PR's head branch and leave the user's uncommitted work untouched (no stash, switch, or overwrite); use a separate worktree when the current checkout is not that branch or is not clean.
  - MUST keep pushed history intact: plain pushes only, and resolve conflicts by merging the base branch in. MUST NOT force push or rebase.
  - MUST make a failing check pass by fixing its cause. MUST NOT skip the check, disable tests, weaken assertions, or use `--no-verify`.
  - MUST stay within the scope of the feedback, and collect user items for the user instead of acting on them.
  - MUST handle each round in this order, because the reply cites the pushed SHA and every push re-runs CI and notifies reviewers:
    1. Fix every code-fix item from the latest `status`/`wait`, then validate locally (format, plus targeted tests or build); done when validation passes.
    2. Commit and push once, through the repo's commit workflow when the context file names one; done when the push succeeds.
    3. Reply on each addressed thread with what changed and the short SHA.
    4. `mark` the handled keys with `--pushed`.
- IF in triage mode:
  - MUST NOT edit files, commit, push, or run builds: the caller shares the checkout and owns code changes.
  - MUST end the turn and return to the caller whenever there are code-fix or user items, or the script reports `stop` or `error`; code-fix items get no reply until the caller pushes.
  - WHEN the caller sends back a pushed SHA for code-fix items, MUST reply on each with what changed and the short SHA, `mark` them with `--pushed`, and resume.
  - WHEN the caller sends back the user's decision on a user item, MUST reply or return it as a code fix accordingly, then `mark` it.

## Preferences

- IF the user wants a watch hands-off, SHOULD run it in a host mode that keeps the session alive unattended (e.g. Copilot CLI `/autopilot`); the loop runs only while the session does.

## Output

- Fix mode: the stop reason (or the script error, or "single pass"), what was addressed with short SHAs, and every item left for the user.
- Triage mode, on each return: `status` (`code_fix | user | stop | error`), the items with their `key`, type, author, location, and requested change, and on `stop` the script's `stop_reason`.

## Verification

- Every surfaced item is marked, listed for the user, or returned to the caller.
- The reported stop reason is the script's `stop_reason` or error, not an inference.
