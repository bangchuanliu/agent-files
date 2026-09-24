---
name: domain-drill
kind: leaf
description: "Three modes for learning any technical domain at staff/principal depth. (1) learn — Socratic L1→L6 session with persistent index. Use when: \"I want to learn X\", \"explore X\", \"map out X\", \"resume learning X\". (2) teach-back — user explains a concept, graded against L1–L6. Use when: \"let me explain X\", \"teach-back on X\", \"grade my understanding\". (3) quick-frame — 5-question problem framing in 2–3 min. Use when: \"frame this\", \"quick frame\", \"think through X\"."
---

# Domain Drill — Staff/Principal Learning

Three modes — read the rubric file before responding.

| Mode | When the user says… | Rubric |
|------|---------------------|--------|
| **learn** | "I want to learn X", "explore X", "map out X", "resume learning X", "what do I still not know about X" | [`modes/learn.md`](modes/learn.md) |
| **teach-back** | "let me explain X", "teach-back on X", "grade my understanding of X", "resume teach-back" | [`modes/teach-back.md`](modes/teach-back.md) |
| **quick-frame** | "frame this: [problem]", "quick frame", "think through X" | [`modes/quick-frame.md`](modes/quick-frame.md) |

**Default**: ambiguous intent → **learn** mode.

### Resume Commands

Paste to continue a saved session:
- `resume learning on [topic]` — e.g., `resume learning on stream processing`
- `resume teach-back on [concept]` — e.g., `resume teach-back on event-time joins`

### Progress Files

```
~/.claude/learning/<topic>/
  index.md                    # learning index (learn mode)
  teach-back-<concept>.md     # per-concept teach-back results
```
