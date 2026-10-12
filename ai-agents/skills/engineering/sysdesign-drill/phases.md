# System Design Drill Phases

The interviewer script for `sysdesign-drill`: the questions and probes for each phase, in the order they run. The protocol rules (role, time box, early exit, phase order, close) are in `SKILL.md`.

Contents: Phase 1 - Find the Tension; Phase 2 - Propose an Architecture; Phase 2.5 - Capacity & API (optional); Phase 3 - Defense Drill + Component Deep-Dive; Phase 4 - Self-Score.

## Phase 1 - Find the Tension (10 min)

Do NOT let the user start proposing architecture. Ask these first.

**Opening question** (after user reads the problem):
> *"Before you name any component or technology: what are they actually asking you to give up? Read the requirements again. What two things can't both be true in this system?"*

If they name a technology instead of a tension, redirect:
> *"You named a tool. I want to hear about a conflict first. What does this system need that is fundamentally at odds with something else it also needs?"*

**Follow-up once they identify a tension:**
> *"Now: which requirement conflicts with another? Can you state the conflict in one sentence - '[X] requires [A] but [Y] requires [B]'?"*

**Closing question for Phase 1:**
> *"If the business had to lose one of these properties entirely - which loss would hurt more? That's your north star. What is it?"*

Once they've made the call: confirm it and move to Phase 2. Do not give them the "right" tension - accept their framing if it's logically sound.

---

## Phase 2 - Propose an Architecture (20 min)

**Opening question:**
> *"You said [tension]. What's the simplest architecture that handles the common case without pretending that tension doesn't exist? Describe the shape - not the tools yet."*

Let them sketch. Then probe the structure:

> *"You described [structure]. Why does that structure exist as a named pattern? What problem does a simpler approach fail to solve here?"*

When they name a pattern, ask:
> *"What does this pattern sacrifice? State it before I find it."*

When they introduce a tool:
> *"Why that tool specifically? What property of the tension does it address that a simpler component wouldn't?"*

If they skip the pattern and jump straight to tools:
> *"You named [tool]. What architectural pattern is that tool implementing? Name the pattern first, then justify the tool."*

**Scale check** (brief, 2 min):
> *"Rough order of magnitude: where does this design hit a wall? What breaks first at 10x load?"*

---

## Phase 2.5 - Capacity & API (OPTIONAL, 10 min)

Ask one question at a time; do not pre-fill numbers - the user must do the math out loud.

**Block A - Capacity (4 min). Make them do BOTE math, not handwave.**

> *"Estimate the read QPS. Start from total users × actions per user per day, then divide. Show your work."*

If they jump to "millions of QPS" without arithmetic:
> *"Slow down. Give me the inputs first: how many users, how often, over what window. Then divide."*

Follow-ups (pick 2 - don't run all):
> *"Write QPS? Reads-to-writes ratio?"*
> *"Storage: bytes per record × records per day × retention. What's a year?"*
> *"Peak vs average. What's your spike multiplier and why?"*
> *"Bandwidth: payload size × QPS. Does that fit one machine's NIC?"*

**Closing capacity question:**
> *"Which number just told you something about the design? Storage, QPS, or bandwidth - which one forces a decision?"*

**Block B - API & Data Model (6 min)**

> *"Name the single most important API endpoint in this system. Give me method, path, request shape, response shape."*

Probe whatever they skip:
> *"What's the auth model on that endpoint? Per-user token, service-to-service, both?"*
> *"What's idempotent and what isn't? How does the client retry safely?"*
> *"Pagination - cursor or offset? Why?"*

Then data model:
> *"Sketch the primary table or document. Fields, primary key, the one or two indices you can't live without."*
> *"What's the access pattern that picked your primary key? If I queried by [secondary field] instead, what does that cost?"*

**Trap to listen for:** They describe a relational schema and then propose a key-value store, or vice versa. Call it out:
> *"Your data model is [relational/document/wide-column]. Your storage choice was [X]. Are those consistent?"*

---

## Phase 3 - Defense Drill + Component Deep-Dive (20 min)

Finish the defense pressure cycle before opening up internals. If Half A finishes early because the user folded or hit every challenge, move to Half B; don't pad.

### Half A - Defense (~10 min)

**Opening:**
> *"Your design has a weak point. Before I find it - where is it?"*

Let them answer. Then apply whichever challenges fit the design:

**Tension violation:**
> *"You accepted [tradeoff X]. Now: what happens when that assumption is violated? Walk me through the failure."*

**Constraint injection:**
> *"A network partition happens between [component A] and [component B]. What does your system do? Is that acceptable?"*

**NFR flip:**
> *"You optimized for [property A]. The product team now says [property B] is non-negotiable. What changes? Does the pattern change, or just the tools?"*

**Scale stress:**
> *"At 10x traffic: what breaks first? Is that a pattern-level problem or a tuning problem?"*

**Hold-your-position check:**
> *"I disagree with your choice of [pattern/tool]. Convince me."*

If they completely abandon their design under challenge: *"You just redesigned from scratch. What made you give up the original approach? Was it a real flaw, or did you lose confidence?"*

### Half B - Component Deep-Dive (~10 min)

Pick ONE component from their design that hides the most complexity (cache, queue, primary store, coordinator, ranker - see `reference.md`). Make them open it up.

**Opening:**
> *"Zoom into [component]. I want to see its internals - not how it talks to others. State, threading, failure mode."*

Probe whichever apply:

**Data structure & state:**
> *"What's the data structure inside? Why that one? What does it cost on insert vs lookup?"*
> *"Where does state live - memory only, memory + disk, replicated? What's lost on crash?"*

**Concurrency:**
> *"Two concurrent writes hit this component at the same key. Walk me through the ordering. Locking, MVCC, CRDTs, or last-write-wins - which and why?"*

**Failure mode:**
> *"This component dies mid-operation. What does the caller see - error, timeout, silent retry? Who is responsible for recovery?"*
> *"Replication: sync or async? What's the failover RPO and RTO?"*

**Hot path:**
> *"Hot key - 1% of keys take 50% of traffic. What does your component do? Shard split, replication, caching layer above?"*

**Bounded resources:**
> *"This component is memory/disk/connection-bound. What's the limit, and what happens when you hit it - backpressure, eviction, refusal?"*

**Closing deep-dive question:**
> *"If I asked you to write the inner loop of this component on a whiteboard right now, could you? If no - that's the gap to study."*

---

## Phase 4 - Self-Score (10 min)

1. *"Did you name the tension or the technology first? Look back at what you said in the first 5 minutes."*

2. *"Did you surface any L2 constraint - something physically or mathematically immovable - before proposing architecture? Or did you jump straight to the pattern?"*

3. *"You named [pattern]. Did you explicitly say what it trades away, or did you leave that for the interviewer to discover?"*

4. *"When I challenged you on [X]: did you hold your position with reasoning, or did you retreat? What was your response?"*

5. (Only if Phase 2.5 ran) *"Your capacity numbers - did the math actually drive a design decision, or were they decoration? Which number changed something?"*

6. *"In the component deep-dive: could you describe the internal data structure, failure mode, and concurrency story? Or did you stay at the box-and-arrow level?"*

7. *"What's the one thing you'd do differently if you started over right now?"*

After they answer all of the above:
> *"Based on your answers - which single dimension was weakest? That's the only thing to practice before your next session. Not 'do more questions' - practice that specific move."*
