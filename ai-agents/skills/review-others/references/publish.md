# Publishing

Step 6's posting mechanics. Reached only after the Step 5 gate returns an explicit affirmative human response; a dry run stops before this file.

## Contents

- [Verdict body template](#verdict-body-template)
- [Inline comment body template](#inline-comment-body-template)
- [Thread reply body template](#thread-reply-body-template)
- [Building the comments array](#building-the-comments-array)
- [Publishing-agent prompt](#publishing-agent-prompt)

## Verdict body template

The top-level review body. Brief by design: per-finding detail lives in the inline comments, so the body carries only the verdict line and, for Mode B, the Resolution Audit.

```
{verdict body line from the Step 6 decision table}

## Resolution Audit (Mode B only - omit otherwise)
{verdicts on prior concerns from Step 4d}

PR HEAD: {HEAD_SHA}
```

## Inline comment body template

```
**[{label}]** {description}

{suggestion if present, fenced as ```suggestion ... ``` if committable}
```

`label` is the short tag you assigned the finding in Step 4c (`bug`, `logic-error`, `security`, `guideline-violation`, `nit`, ...). Render it verbatim.

## Thread reply body template

```
{description}

- in reply to @{thread_reply_reviewer}'s comment.
```

## Building the comments array

One comment object per finding with no `thread_reply_to`. `path` is relative to the repo root, matching `gh pr diff`. The line numbers come from the finding's `line`:

| Finding `line` | Comment object |
|---|---|
| `L42` (single line) | `{"path": "...", "side": "RIGHT", "line": 42, "body": "..."}` |
| `L29-L31` (range) | `{"path": "...", "start_side": "RIGHT", "start_line": 29, "side": "RIGHT", "line": 31, "body": "..."}` |

`side` is always `"RIGHT"`: anchors only ever land on added lines, which live in the post-change file.

## Publishing-agent prompt

Dispatch **one agent per confirmed PR, all in a single message**. Each agent posts the thread replies first, then the top-level review carrying every new inline finding in `comments[]`.

````
Post a GitHub PR review for PR {PR_NUMBER} in {REPO}.

Step 0 - Revalidate the target BEFORE any write. The author may have pushed, force-pushed,
closed or merged while the review ran or while confirmation was pending:
  gh pr view {PR_NUMBER} --repo {REPO} --json state,headRefOid
  If `state` != "OPEN", or `headRefOid` != "{HEAD_SHA}" (the reviewed SHA): post NOTHING -
  not the thread replies, not the review - and report "PR moved on (state=X, head=Y);
  re-review required". Never post a stale review against a revision nobody reviewed.

Step 1 - Post {K} thread reply(ies) (skip if K=0). For each:
  gh api repos/{REPO}/pulls/{PR_NUMBER}/comments --method POST \
    -F in_reply_to={top_id} \
    -f body="{thread_reply_body}"

Step 2 - Post the top-level review with inline comments in one atomic call:
  cat > /tmp/review_{PR_NUMBER}.json <<'EOF'
  {
    "commit_id": "{HEAD_SHA}",
    "event": "{APPROVE|COMMENT}",
    "body": "{verdict body - short, no per-finding lists}",
    "comments": [
      {"path": "...", "side": "RIGHT", "line": 42, "body": "**[bug]** ..."},
      {"path": "...", "start_side": "RIGHT", "start_line": 29, "side": "RIGHT", "line": 31, "body": "**[nit]** ..."}
    ]
  }
  EOF
  gh api repos/{REPO}/pulls/{PR_NUMBER}/reviews --method POST --input /tmp/review_{PR_NUMBER}.json

The `comments` array is GitHub's standard inline-review mechanism - each entry becomes an inline file comment on the cited line(s). If `comments` is empty `[]`, the review posts with only the verdict body (LGTM case).

A `422 Unprocessable` is not always an anchoring failure - it is also what a changed head or a closed PR looks like. On 422: re-run Step 0's `gh pr view`. If state/head moved, stop and report; do not retry. If the PR is still open at the reviewed SHA and GitHub's error names a specific `comments[i]` path/line, drop that one comment and re-post once. If the error names nothing specific, stop and report the payload and error verbatim - never guess which finding to drop, and never fall back to embedding findings in the verdict body.

Report success for each call, or the error message if any fails.
````
