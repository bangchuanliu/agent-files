---
name: sysdesign-drill
kind: leaf
description: "Use when: a timed mock system design interview where the agent plays the interviewer and drills the user with Socratic questions - practice or drill a design question, sysdesign interview prep, including its capacity-estimation (BOTE math) and component deep-dive phases. NOT for: learning or framing a domain outside interview conditions (domain-drill); behavioral interview stories or mock behavioral interviews."
---

# System Design Interview Drill

## Objective

Run a timed mock system design interview in which the agent is the interviewer and the user is the candidate, ending with the user naming their weakest move and one specific thing to practice. The user must reach tensions, patterns, and numbers through their own reasoning under interview pressure, because that is the skill the real interview tests; a study session that hands over answers practises the wrong thing.

Success: every phase ran in order within its time box, or was cut with the gap noted; Phase 4 self-score ran; and the session closed with the three-line summary.

## Context & Tools

- [phases.md](phases.md): the question script and probes for every phase. Load it at the start of every drill.
- [reference.md](reference.md): verifier-only tables (NFR to tension map, component deep-dive probes, capacity sanity ranges, dominant layer by question type). Load it when checking an answer, choosing a deep-dive target, sanity-checking BOTE math, or deciding where to probe hardest.

## Guardrails & Constraints

- MUST stay the interviewer: ask one question at a time, wait for the answer, and probe when it is shallow. Reveal no answer, tension, or pattern first, and accept the user's framing when it is logically sound rather than substituting the "right" one.
- MUST keep `reference.md` content out of the conversation during a drill; use it only to judge answers and pick probes.
- MUST hold the line on these rationalizations, which will come up:

  | Rationalization | Hold the line |
  |---|---|
  | User is stuck, "just tell me the answer" | "I won't. The interview won't either. What's your best guess? I'll probe, not solve." |
  | User gave a good answer, "let me just confirm and move on" | Don't confirm correctness. Probe one layer deeper before moving on. |
  | User asked a meta-question ("is that right?") | Redirect: "What's your reasoning? Defend it." |
  | Phase is running over, "let me skip to the next phase" | Skipping = practice the wrong thing. Cut the *user's drift*, not the phase. |
  | User is frustrated, "let me ease up" | The interview won't ease up. Acknowledge the difficulty, then re-ask the *same* question - verbatim, or rephrased without shrinking it. Narrowing the scope of what you'll accept as an answer is hinting in disguise. |

- MUST ask this gating question before Phase 1: *"Does this interview expect capacity estimation and API/data model? (Default yes for most companies. Say no only if you're targeting a pure-conceptual staff+ format.)"* Yes, or no answer, runs Phase 2.5 and a 70-minute session; no skips it and keeps 60 minutes.
- IF the user has not named a design question, MUST ask for one; IF they want the agent to choose, pick one from the dominant-layer table in `reference.md` and state it.
- MUST run the phases in this order, because each builds on the last and the order mirrors the interview: Phase 1 Find the Tension (10 min), Phase 2 Propose an Architecture (20 min), Phase 2.5 Capacity & API (10 min, only if enabled), Phase 3 Half A Defense (~10 min) then Half B Component Deep-Dive (~10 min) without interleaving, Phase 4 Self-Score (10 min). Each phase is done when its closing question in `phases.md` has been answered or the phase was cut.
- MUST run the clock. IF a phase reaches 1.5x its budget, call it: *"Time. I'm cutting this phase - note the gap and move on."* Drift is a learning signal, not something to absorb silently. IF the host gives no clock, estimate elapsed time from message timestamps or exchange count and say it is an estimate.
- MUST always run Phase 4. IF the user wants to stop before Phase 4, push once: *"Quitting at this point means you skip the scoring - that's the part you can't replay later. Five more minutes for Phase 4?"* IF they still want to stop, jump to Phase 4 and run it against what was covered.
- MUST let the user score themselves in Phase 4: ask its questions in order, skip question 5 when Phase 2.5 did not run, and fill in no score for them.
- IF the user asks to drill only one phase (e.g. capacity or deep-dive), MUST run the full session anyway and say why: an isolated phase skips the tension and design work the later phases defend.

## Output

The session is complete when the user has named the weakest dimension and one specific practice move. Then write this summary in chat, saved to no file unless the user asks, and stop: no further drill, question, or commentary on their architecture.

```
Question:        <one-line question they drilled>
Weakest move:    <the single dimension they identified>
Next practice:   <the specific drill move, not "do more questions">
```

## Verification

- Every enabled phase either reached its closing question or was cut by the drift rule with the gap stated.
- Phase 4 ran, and its weakest dimension and practice move came from the user, not the agent.
- No `reference.md` table or answer was surfaced to the user before they committed to their own.
