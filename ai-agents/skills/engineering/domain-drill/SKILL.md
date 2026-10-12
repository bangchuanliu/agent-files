---
name: domain-drill
kind: leaf
description: "Use when: Socratic drilling of a technical domain to staff/principal depth across layers L1-L6 - learning or resuming a domain X (learn); explaining X back to be graded (teach-back); framing one problem in 2-3 minutes (quick-frame). NOT for: system-design interview practice (sysdesign-drill); building a visual study dashboard for a topic; self-review (self-assessment), peer feedback (peer-feedback), or Slack drafts (slack-msg)."
---

# Domain Drill

## Objective

Drill the user through a technical domain with questions so they build, and can prove, their own staff/principal-level model of it: the forces that created it (L1), hard constraints (L2), core tensions (L3), architectural patterns (L4), where tools sit (L5), and the implementation knobs that encode the tensions (L6). The user does the reasoning because insight read from the agent does not transfer; the agent asks, probes, and records.

Success: the chosen mode ran to its completion criterion below, and any progress it saves is in the user's words and can be resumed next session.

## Context & Tools

Pick one mode and load only its file, which holds the question sequence, probes, rubric, and save format:

| Mode | Use for | Done when |
|------|---------|-----------|
| [learn](modes/learn.md) | Socratic L1-L6 learning map for a domain, new or resumed. | The session's layers are captured in the index, and the validation warning and backlog (the model came partly from an AI that can be confidently wrong) and next focus are recorded. |
| [teach-back](modes/teach-back.md) | The user explains a concept; grade transfer against L1-L6. | Grade saved with strengths, gaps, inversions, score, and next drill focus. |
| [quick-frame](modes/quick-frame.md) | 2-3 minute framing of one specific problem. | The three-line constraint / tension / direction summary is given. |

## Guardrails & Constraints

- MUST make the user commit to an answer before confirming, correcting, or revealing anything, and follow the reveal and no-hint rules of the active mode, because the drill's value is the user's own reasoning.
- MUST record the user's articulation, not the agent's, in any saved index or grade, so the file reflects what the user actually knows.
- MUST name only papers, talks, people, or systems the agent is confident exist; IF unsure, say so and ask the user to verify instead of inventing a citation.
- IF the mode is ambiguous, MUST default to learn mode.
- IF the topic, or the concept for teach-back, is missing, MUST ask for it before starting.
- MUST keep progress under `learning/<topic>/` in this skill's directory (`$SKILL_DIR` in the mode files) unless the user names another persistent location. IF the host does not define `$SKILL_DIR`, resolve it as the directory containing this `SKILL.md`.
- WHEN updating an existing index or teach-back file, MUST keep prior coverage and open questions and update them in place, because the file is the only memory across sessions.

## Verification

- The active mode's "Done when" criterion above holds.
- IF the mode saves progress, the file exists at the stated path, follows the mode's format, and still contains the prior session's content when one existed.
- IF the session ended early, say which layer or question it stopped at and record that as the next focus.
