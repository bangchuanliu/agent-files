---
name: review-others
kind: orchestrator
agents: claude, copilot
description: "Use when: reviewing someone else's GitHub PR and posting the review inline - one PR from a link or ref, a batch of open PRs awaiting your review, a re-review after the author addressed your comments, or any of these as a dry run that only prints. NOT for: feedback or failing checks on your own PR."
---

# Review Others' PRs

## Objective

Review other people's open PRs and post each review on GitHub as inline comments with an approve-or-comment verdict, so authors get anchored, classified findings without a confirmation round-trip. Scope is one PR (link or ref given) or a batch of at most 10 (no ref given); a follow-up re-reviews only what changed since your last review.

Done when every PR in scope has either a posted review (or, in a dry run, a printed one) or a stated skip reason, and every finding is classified and anchored on an added line.

## Guardrails & Constraints

### Scope and access

- **Ref given** (URL, `org/repo#123`, `#123`): review exactly that PR. A bare `#123` refers to the current repo.
- **No ref given (batch):** queue at most 10 eligible open PRs from the target repo (the current repo, or one the user named), PRs requesting your review (`review-requested:@me`) first. IF there is no current repo and none was named, MUST ask.
- MUST address the PR through its **base** repo; a fork's head repo is the wrong `/pulls/` endpoint.
- MUST make every GitHub call through `gh`. IF a call fails (auth, rate limit, 422), MUST stop and report rather than continue on partial data.
- MUST read the PR remotely (`gh pr diff`, `gh pr view`) and leave the local working tree untouched, because the user may have unrelated work in progress there.

### Eligibility

A PR is reviewed only when all three hold. In batch mode skip a PR that fails one; with a ref, report the failing rule and stop.

- **Someone else's:** the author differs from `gh api user --jq .login`.
- **Open and ready:** not closed, merged, or draft.
- **Clear of your open comments:** you have no prior comments on it, or every one is **addressed** - resolved, replied to by someone else, or its lines changed in a commit after your last review.

### Reviewing

- MUST apply the repo's own rules first: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (whichever exist), plus any review context your instructions provide for this skill.
- IF this is a follow-up, MUST review only the diff from your last reviewed commit to head (`gh api repos/{repo}/compare/{last}...{head}`) and confirm each earlier comment was actually fixed.
- MUST read existing comments first and defer to earlier reviewers: a concern already raised is theirs; reply in their thread only when you add something new.
- MUST classify every finding as `blocking`, `minor`, or `nit`, and report only what the diff confirms. A `blocking` finding names a concrete failure mode or quotes a rule.
- IF the host has Copilot CLI's built-in `code-review` agent, MUST delegate each PR's review to it with model `gpt-6.1-sol`.
- Because `code-review` reviews the local tree, not the PR, the parent MUST first fetch the PR via `gh` (diff or follow-up compare diff, PR metadata, existing comments, repo rules) and pass it in the prompt, telling the agent to review only the supplied diff and return classified `file:line` findings. The parent then posts.
- IF the host has no `code-review` agent (e.g. Claude), MUST use a general-purpose subagent instead; hosts without subagents review in sequence.
- IF reviewing a batch, SHOULD fan out one reviewer agent per PR, launched together.

### Posting

- Posting is direct, with no confirmation prompt; that is the intended behaviour. IF the user asks for a **dry run** ("dry run", "don't post", "review only", `--no-post`), MUST write nothing to GitHub and only print.
- MUST post every finding inline at its `file:line`; the review body carries only the verdict line.
- MUST anchor each comment on an added line (`+` in the diff, `side: RIGHT`), because GitHub rejects any other line with 422. Point at the line the concern is about, which is often not the first added line of the hunk.
- MUST post the verdict and all findings in one `POST repos/{repo}/pulls/{n}/reviews` call with a `comments[]` array. Thread replies go through `POST repos/{repo}/pulls/{n}/comments` with `in_reply_to`.
- MUST set the verdict over all findings, thread replies included:

  | Findings | Event | Body |
  |---|---|---|
  | none | `APPROVE` | `LGTM.` |
  | only `nit` | `APPROVE` | `LGTM, {N} minor comment(s) inline.` |
  | any `minor`, no `blocking` | `COMMENT` | `{N} minor issue(s) inline.` |
  | any `blocking` | `COMMENT` | `{N} blocking issue(s) inline.` |

## Output

One block per PR, then a one-line tally (`{N} approved, {N} commented, {N} skipped`):

```
## PR #123 - {title} (@author) - {Initial | Follow-up} - {Approved | Commented | Skipped: reason | Dry run}
- [blocking] path/to/file.py:L42 - description
- [minor]    path/to/file.py:L88 - description
Prior comments: {N addressed / N total}   # follow-up only
```

## Verification

- Every PR in scope appears in the output with a posted verdict, a dry-run print, or a skip reason naming the failed eligibility rule.
- Every posted comment's line is an added line in the reviewed diff, shown by the review POST succeeding without 422.
- In a dry run, no `gh` write call was made.
