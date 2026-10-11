---
name: self-assessment
kind: leaf
description: "Self-review impact framing for the user's own work: score a PR description, design doc, journal note, weekly write-up, or Slack thread against 11 career principles and rewrite it with quantified impact. Use when: self-assessment, self-review, promo write-up, weekly review, daily journal review, how do I describe this work, rewrite this for impact, career self-evaluation. NOT for: feedback about a colleague - use peer-feedback; outgoing Slack/IM drafts - use slack-msg."
---

# Self-Review Reframe

Score an artifact about the user's own work against the 11 career principles, then rewrite demonstrated principles as impact-first bullets.

Source of truth: read [`principles.md`](principles.md) before scoring. It defines the principles, evidence signals, bullet formats, impact categories, and anti-patterns.

## Process

1. **Read the artifact.** Accept pasted text, a file path, a PR URL, or a journal/weekly section. If multiple artifacts are provided, score each separately and aggregate gaps.
2. **Choose scope.** Default is all 11 principles. Optional flags: `--exec-only` for E1-E3, `--no-craft` for L+E, `--craft-only` for C1-C5, `--weekly <file>` for multiple artifacts.
3. **Score every in-scope principle.** Use `✓` only when the artifact has a concrete supporting sentence and impact is named. Use `⚠` for vague, implied, or impact-missing evidence. Use `✗` when absent. Quote the artifact verbatim for `✓` and `⚠`.
4. **Reframe every `✓` and `⚠`.** Use the BAD to GOOD patterns in `principles.md`. Preserve the user's vocabulary and numbers. Insert `[quantify: <metric>]` when no number exists.
5. **Flag every `✗`.** Give one concrete prompt from that principle's "Look for" list.
6. **Call out exec-only shape.** If all leadership rows are `✗`, state that the artifact is strictly execution scope and ask whether a leadership angle was left out.

## Output

Write in chat unless the artifact has more than three sections or the user asks for a saved file. If saving, write under `self-assessment/reports/` in the current workspace or another user-specified persistent path.

```markdown
# Self-Review: <artifact title>

## Coverage
| Principle | Status | Evidence |
|---|---|---|
| L1 Direction Setting | ✓/⚠/✗ | "<quote or ->" |
...

## Reframed (impact-first)
**<Code> - <Principle>**
> <drop-in replacement with quantified impact or [quantify: ...]>

## Gaps - what to add next time
- **<Code> <Principle>**: <one-line concrete prompt>

## Verdict
<Strong / partial / exec-only, with the leadership-angle question when relevant.>
```

## Rules

- Use the 11 principle names from `principles.md` exactly.
- Quote evidence, not paraphrases.
- Keep every reframe impact-first and drop-in ready.
- Use placeholders instead of invented numbers.
- Match the artifact register: technical for PRs, outcome-driven for promo docs, first-person for journals.
