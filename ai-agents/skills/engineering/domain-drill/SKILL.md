---
name: domain-drill
kind: leaf
description: "Learn a technical domain at staff/principal depth. Use when: I want to learn X, explore X, map out X, resume learning X. Teach-back: grade the user's explanation against L1-L6. Use when: let me explain X, teach-back on X, grade my understanding. Quick-frame: 5-question problem framing in 2-3 minutes. Use when: frame this, quick frame, think through X. NOT for: system-design interview practice - use sysdesign-drill; self-review, peer feedback, or Slack message drafting."
---

# Domain Drill

Pick one mode, read the linked rubric, then run only that mode.

| Mode | Use for | Completion |
|------|---------|------------|
| **learn** | Socratic L1-L6 learning map for a technical domain. | Current layer captured and next focus recorded. |
| **teach-back** | The user explains; you grade transfer against L1-L6. | Grade saved with strengths, gaps, score, and next drill focus. |
| **quick-frame** | 2-3 minute framing for one problem. | Three-line constraint/tension/direction summary. |

Rubrics:
- [`modes/learn.md`](modes/learn.md)
- [`modes/teach-back.md`](modes/teach-back.md)
- [`modes/quick-frame.md`](modes/quick-frame.md)

Default: ambiguous intent means **learn** mode.

Progress storage: use `learning/<topic>/` inside this skill directory unless the user names another persistent location. Keep paths portable across host agents.
