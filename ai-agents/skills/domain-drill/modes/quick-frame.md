# Quick Frame Mode

**Purpose**: 2–3 minute structured framing for a specific problem. Five questions, one exchange each. No index update. No deep probing.

Extract the problem from the user's message. Ask each question applied to that specific problem — never the generic version.

---

### Q1 — Hard Constraint

*"In [this specific system], what is the one reality that no amount of engineering can eliminate — the property of the environment every solution must accept as given?"*

If the answer names a technology limitation, probe once: *"Is that truly immovable, or is it a current limitation that better tooling could solve in a few years?"*

---

### Q2 — Core Tension

Push to an extreme first. Let the tension emerge from the user's reasoning, not from the question structure:

*"What would it take to guarantee [desired property from Q1 answer] completely — at any cost? What would you need to store, track, or coordinate, and what happens to your system as that grows without bound?"*

When they hit the wall, ask: *"So what are the two properties pulling against each other? Name it in three words: [A] vs [B]."*

---

### Q3 — Architectural Direction

*"If you optimize purely for [A] — push it to the maximum — what does the system shape look like? Describe the structure, not the tools."*

---

### Q4 — Failure Modes

*"What breaks if you push too far toward [A]? What breaks if you push too far toward [B]? Is one failure mode significantly worse than the other?"*

---

### Q5 — Technology Fit

*"Given that constraint and tension: why does [candidate approach] fit here better than [obvious alternative]? What specific property of the tension does it address that the alternative can't?"*

---

**Close** — summarize in three lines, then stop:

```
Constraint: [one sentence]
Tension:    [A] vs [B] — worse failure is [side]
Direction:  [architectural shape] because [constraint reason]
```

If a learning index exists at `~/.claude/learning/<topic>/index.md`, offer to append under `## L3 — Core Tensions` or `## Open Questions`.
