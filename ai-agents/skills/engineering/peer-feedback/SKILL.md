---
name: peer-feedback
kind: leaf
description: "Use when: turning rough notes about a colleague into a truthful, strength-led peer-feedback document (Context, Strengths, one Growth and Development note, Overall Assessment) - write peer, 360, calibration, or performance-review feedback for a coworker; polish an existing peer-feedback draft. NOT for: self-assessment or promo writing about the user's own work (self-assessment); reviewing a colleague's code or PR (review-others); outgoing Slack or IM drafts (slack-msg)."
---

# Peer Feedback

## Objective

Turn the user's notes or draft about a colleague into a peer-feedback document, under 600 words, that a reviewer who knows neither person can trust and act on. It is a real document about a real person entering a real review, so every strength is a concrete instance with its impact, every specific is one the user supplied or confirmed, and growth is one thin, positive, forward-looking stretch.

Success: the document follows the template in [reference.md](reference.md), passes the checks under Verification, and is saved where the user can find it.

## Context & Tools

- [reference.md](reference.md): the output template, section craft, values guidance, what to leave out, phrase bank, and a worked example. Read it before writing or polishing.

## Guardrails & Constraints

- MUST use only confirmed specifics: every project, metric, and accomplishment comes from the user's material or the user's answer, with the user's numbers preserved exactly. IF a strength needs a number or example that is missing, ask; IF still missing, flag the spot for the user instead of filling it. A plausible invented metric is the most damaging thing this skill can produce.
- MUST interview once before drafting, in one batched set of questions covering only what is missing: colleague name, review period (`YYYY-MM`), reviewer, working relationship, concrete examples, outcomes, metrics, and the next-level stretch. Wait for the answers, because the draft is only as good as the specifics behind it. IF the user cannot answer, draft with each gap visibly flagged.
- MUST drop a strength that is still only a general trait after the interview, rather than polish the trait.
- MUST keep the document at 600 words or fewer.
- IF the user provides a draft that is already close, MUST polish it against the same rules and reference: vague praise becomes examples, growth compresses to one forward-looking note, at least one strength ties to an organizational value, and anything on the reference's leave-out list goes.
- MUST save as `{name}_{YYYY}_{MM}.md` in the folder the user names; otherwise in `$PEER_FEEDBACK_DIR` when set; otherwise in `peer-feedback/` in the current workspace. IF that file already exists, ask before overwriting.
- MUST keep the document local; IF the user asks to post it to a shared system (doc, review tool, chat), confirm before writing there, because it is personal feedback about a named colleague.

## Output

- The saved file path.
- Each place that would land better with a number or a concrete example, and each gap flagged because the user could not supply it.

## Verification

- Every project name, metric, and accomplishment in the document traces to the user's notes or answers.
- Every strength bullet names a concrete instance a reader could picture, plus its impact.
- Growth and Development is one or two positive, forward-looking sentences; at least one strength and the growth note tie to an organizational value, or to the named behavior when no value list is available.
- No personality judgments, peer comparisons, or speculation about motives.
- Word count is 600 or fewer.
