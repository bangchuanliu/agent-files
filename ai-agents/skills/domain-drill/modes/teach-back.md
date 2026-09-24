# Teach-Back Mode

**Purpose**: Validate that learning transferred. The user explains a concept; grade it against the L1–L6 framework. Exposes what they think they know vs. what they actually understand.

---

## Session Start

Check `~/.claude/learning/<topic>/teach-back-<concept>.md`:
- **File exists**: read it, say *"Last time you got [strong areas] right but had gaps in [weak areas]. Want to try again or continue from where you left off?"*
- **File missing**: say *"Go ahead — explain [concept] as you understand it. Don't look anything up. I'll grade you after."*

---

## How to Receive the Explanation

Let the user finish without interrupting. Do not prompt or hint mid-explanation. When they stop, grade against these five dimensions:

| Dimension | What to check | Weight |
|-----------|--------------|--------|
| **Constraints first** | Did they ground the concept in L2 constraints before naming solutions? Or did they jump straight to technology? | High |
| **Tensions named** | Did they identify the core L3 tradeoff? Can they name the failure modes at each extreme? | High |
| **Architecture derived** | Did they show how the L4 pattern follows from the tension, or did they state the pattern as a given? | Medium |
| **Technology in context** | Did they explain WHY a technology fits here, or just name it? Did they acknowledge context-dependence? | Medium |
| **Counter-movements** | Did they mention forces that could challenge or reverse the current direction (L1 counter-movement)? | Low |

---

## Output Format

Always use this structure:

```
## Teach-Back: [Concept] — [Date]

### What you got right
- [specific strength, with the L-layer it maps to]

### Gaps
- [missing piece] — you said [X] but the actual constraint/tension is [Y]

### Inverted
- [anything stated backwards or causally wrong]

### Score
Constraints-first:    [✓ / ~ / ✗]
Tensions named:       [✓ / ~ / ✗]
Architecture derived: [✓ / ~ / ✗]
Technology in context:[✓ / ~ / ✗]

### Next drill focus
[one specific L-layer or concept to strengthen before the next teach-back]
```

---

## After Grading

Save result to `~/.claude/learning/<topic>/teach-back-<concept>.md` and offer to push gaps into the main learning index under `## Open Questions`.

**If the explanation is strong across all dimensions**: say so directly, then challenge with one harder question — a counter-movement, an edge case, or a context where the standard tradeoff flips.
