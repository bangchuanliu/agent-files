---
name: review-others
kind: orchestrator
agents: claude, copilot
description: "Use when: reviewing someone else's PR from a link or ref, batch-reviewing open PRs awaiting your review, re-reviewing a PR after the author addressed your comments. NOT for: your own PR -> use review-self."
---

# Review Others' PRs

Rules for choosing which PRs to review, reviewing them, and posting inline. Order the work however you like.

**Done when** every PR in scope has either a posted review or a stated skip reason, and every posted finding is classified and anchored on an added line.

## Scope

- **PR link or ref given** (URL, `org/repo#123`, `#123`): review exactly that PR.
- **No ref given**: batch mode. Queue **at most 10** open PRs from the target repo (the current repo, or one the user named) that pass eligibility, PRs requesting your review (`review-requested:@me`) first.
- The PR's **base** repo owns it; a fork's head repo is the wrong `/pulls/` endpoint.
- Every GitHub call goes through `gh`. When one fails (auth, rate limit), stop and report rather than continue on partial data.

## Eligibility

A PR is reviewed only when all three hold. Batch mode skips a PR that fails one; with a PR link, report the failing rule and stop.

- **Someone else's.** The author differs from `gh api user --jq .login`.
- **Open and ready.** Not closed, merged, or draft.
- **Clear of your open comments.** You have no prior comments on it, or every one is **addressed**: resolved, replied to by someone else, or its lines changed in a commit after your last review.

## Local context

Read `~/.agents-local/docs/skill-context/review-others/context.md` if it exists; it may add review
guidelines for specific repositories. Its absence is normal.

## Reviewing

- **Remote only.** Read the PR through `gh pr diff` and `gh pr view`; the local working tree stays untouched.
- **Batch fans out**: one subagent per PR, launched together, each reading the PR via `gh`. Pick a general-purpose subagent, because Copilot CLI's built-in `code-review` reviews the local tree instead of the PR. Hosts without subagents review the queue in sequence.
- **The repo's rules come first**: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, whichever exist, plus anything the local context above adds.
- **Follow-ups are incremental.** Review the diff from your last reviewed commit to head (`gh api repos/{repo}/compare/{last}...{head}`), and confirm each earlier comment was actually fixed.
- **Defer to earlier reviewers.** Read existing comments first. A concern already raised is theirs; add a reply in their thread only when you bring something new.
- **Classify every finding** as `blocking`, `minor`, or `nit`. `blocking` names a concrete failure mode or quotes a rule. Report only what the diff confirms.

## Posting

- **Inline only.** Each finding posts at its `file:line`; the review body carries just the verdict line.
- **Anchor on added lines** (`+` in the diff, `side: RIGHT`): GitHub rejects any other line with 422. Point at the line the concern is about, which is often not the first added line of the hunk.
- One `POST repos/{repo}/pulls/{n}/reviews` call carries the verdict plus a `comments[]` array. Thread replies go through `POST repos/{repo}/pulls/{n}/comments` with `in_reply_to`.
- **Verdict** (over all findings, thread replies included):

  | Findings | Event | Body |
  |---|---|---|
  | none | `APPROVE` | `LGTM.` |
  | only `minor` / `nit` | `APPROVE` | `LGTM, {N} minor comment(s) inline.` |
  | any `blocking` | `COMMENT` | `{N} blocking issue(s) inline.` |

- **Posting is direct**, with no confirmation prompt. A **dry run** ("dry run", "don't post", "review only", `--no-post`) writes nothing to GitHub and only prints.

## Output

One block per PR, then a one-line tally (`{N} approved, {N} commented, {N} skipped`):

```
## PR #123 - {title} (@author) - {Initial | Follow-up} - {Approved | Commented | Skipped: reason | Dry run}
- [blocking] path/to/file.py:L42 - description
- [minor]    path/to/file.py:L88 - description
Prior comments: {N addressed / N total}   # follow-up only
```
