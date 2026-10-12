---
name: self-assessment
kind: leaf
description: "Use when: scoring an artifact about the user's own work - PR description, design doc, journal note, weekly write-up, or Slack thread - against 11 career principles and rewriting it as impact-first, quantified bullets - self-assessment or self-review of a piece of work, promo bullets, how do I describe this work, rewrite this for impact; weekly or daily journal review across several artifacts. NOT for: feedback about a colleague (peer-feedback); outgoing Slack or IM drafts (slack-msg); synthesizing a whole review-period self-assessment document across projects."
---

# Self-Review Reframe

## Objective

Score an artifact about the user's own work against the 11 career principles in [principles.md](principles.md) and rewrite what it demonstrates as impact-first bullets the user can drop into a review, so the work reads as leadership, execution, and craft with quantified impact instead of a task list. Every score is grounded in a verbatim quote, every reframe keeps the user's own vocabulary and numbers, and every gap gets a concrete prompt for what to add next time.

Success: every in-scope principle has a status backed by evidence, every `✓` and `⚠` has a reframe, every `✗` has a prompt, and nothing in a reframe is invented.

## Context & Tools

- [principles.md](principles.md): the principles, bullet formats, quantification tiers, evidence signals ("Look for"), BAD to GOOD patterns, and anti-patterns. Read it before scoring.

## Guardrails & Constraints

- MUST score every in-scope principle, using the 11 principle names and codes from `principles.md` exactly:
  - `✓` only when the artifact has a concrete supporting sentence and names the impact;
  - `⚠` when the evidence is vague, implied, or missing impact;
  - `✗` when absent.
- MUST quote the artifact verbatim, not paraphrase, as the evidence for each `✓` and `⚠`, so the user can see exactly what earned the score.
- MUST reframe every `✓` and `⚠` as a drop-in, impact-first bullet in its principle's format, preserving the user's vocabulary and numbers. Numbers come only from the artifact, from arithmetic on its numbers, or from an estimate the artifact supports, marked `~`; otherwise insert `[quantify: <metric>]`, because an invented number in a review document misrepresents the user's work.
- MUST give each `✗` one concrete prompt drawn from that principle's "Look for" list.
- IF every in-scope leadership principle is `✗`, MUST say the artifact is strictly execution scope and ask whether a leadership angle was left out.
- Scope defaults to all 11 principles. IF the user passes a flag, MUST honour it: `--exec-only` scores E1-E3, `--no-craft` scores L and E, `--craft-only` scores C1-C5, and `--weekly <file>` or several artifacts scores each artifact separately, then aggregates the gaps.
- IF the artifact is missing, or a PR URL or file cannot be read, MUST ask the user to paste it instead of scoring from memory or a guess.
- IF saving a report, MUST write under `self-assessment/reports/` in the current workspace or the path the user names; ask before overwriting an existing report.

## Preferences

- SHOULD match the artifact's register: technical for PRs, outcome-driven for promo docs, first-person for journals.

## Output

Write in chat, unless the artifact has more than three sections or the user asks for a file. Default layout, which the agent may adapt when it serves the user better:

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

## Verification

- Every in-scope principle appears once with a status; every `✓` and `⚠` quote appears verbatim in the artifact.
- Every reframe closes with a number from the artifact, a `~` estimate grounded in it, or a `[quantify: ...]` placeholder.
- Every `✗` has a prompt; the exec-only callout is present when its condition holds.
