# Batch queue

Step 2's batch branch and Step 3's announcement. Reached only when argument tokenization left **no** single-PR reference; a run that named a PR never opens this file.

## Resolve the repo

From the remaining positional argument:

| Positional argument | `REPO` |
|---|---|
| Contains `/` (`owner/repo`) | use as-is |
| Bare name and `REVIEW_DEFAULT_ORG` is set | `$REVIEW_DEFAULT_ORG/{name}` |
| Bare name and no default org | stop with a one-line error: rerun as `owner/repo` or set `REVIEW_DEFAULT_ORG` |
| Empty | `gh repo view --json nameWithOwner -q .nameWithOwner` |

## Fetch the candidates

Fetch up to 100 open, non-draft PRs with the query for the mode. If the input was a bare name, resolve it first using `REVIEW_DEFAULT_ORG`, then use the default requested-reviewer query against the resolved repo:

| Mode | `gh pr list` search flags |
|------|--------------------------|
| **Default** (requested reviewer) | `--repo {REPO} --search "is:open review-requested:@me -is:draft"` |
| **all** | `--repo {REPO} --state open --search "-is:draft"` |
| **--author** | `--repo {REPO} --state open --author {AUTHOR} --search "-is:draft"` |

Always append `--json number,title,author,url,headRefOid,updatedAt,isDraft --limit 100`.

## Post-fetch pipeline

Apply in order: drop `author.login == MY_LOGIN` -> apply the already-reviewed filter below -> cap at `REVIEW_LIMIT` (default 20, or `--limit=N`).

`--limit` caps how many PRs are **reviewed**, not how many are fetched. Always fetch up to 100, then cap after filtering.

If no PRs remain, report `No open PRs to review` and stop.

## Filter: skip already-reviewed PRs

For each PR, fetch your own reviews and the comment graph:

```bash
gh api repos/{REPO}/pulls/{PR_NUMBER}/reviews --jq '[.[] | select(.user.login == "MY_LOGIN")]'
gh api repos/{REPO}/pulls/{PR_NUMBER}/comments --jq '[.[] | {id, user: .user.login, in_reply_to_id}]'
```

| Condition | Action |
|-----------|--------|
| You have an APPROVED review | **Skip** - already approved |
| You have comments with no replies yet | **Skip** - waiting for author response |
| You have no reviews and no comments | **Review** |
| You have comments that have been replied to, but no approval | **Review** - re-evaluate |

A comment is unreplied when no other user's comment carries an `in_reply_to_id` equal to that comment's `id`.

Stop the filter loop as soon as `REVIEW_LIMIT` PRs are selected, leaving the remaining candidates unchecked.

If nothing survives the filter, report `All PRs already reviewed or awaiting replies` and stop.

Cache both full responses: Step 4b partitions the same payloads by `user.login != MY_LOGIN` instead of calling the endpoints again.

## Step 3: announce the queue

Print the table and proceed straight into Step 4 - the queue is informational, and Step 5 is the only gate.

```
Found N open PRs in {REPO} (M to review, K skipped):

| # | PR | Author | Title | Status |
|---|-----|--------|-------|--------|
| 1 | #123 | @alice | Add retry logic | Reviewing / Skipped - approved / Skipped - awaiting reply |
```
