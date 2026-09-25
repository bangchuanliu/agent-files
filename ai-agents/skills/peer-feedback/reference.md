# Peer Feedback Reference

The output template, the rules that make feedback land, and a worked example of
turning rough notes into a finished document.

## Table of contents
- [Output template](#output-template) - the exact structure to produce
- [Section craft](#section-craft) - how to write each section well
- [DO / Guardrails](#do--guardrails) - the rules that separate useful feedback from filler
- [Phrase bank](#phrase-bank) - openers when you're stuck
- [Worked example](#worked-example) - rough project notes -> finished doc

---

## Output template

Produce exactly this structure, **600 words or fewer total**. Keep the `---` separators  - 
they make the doc skimmable in a review tool. The sections map onto three common
feedback prompts: Strengths answers *"how does this person demonstrate our values?"*, Growth and Development answers *"how can they continue to grow and develop?"*,
and Overall Assessment answers *"what has been their impact, and how can it be deepened?"*

```markdown
# Peer Feedback

**Employee Name:** {Name}
**Review Period:** {YYYY-MM}
**Reviewer:** {Reviewer}
**Working Relationship:** {one line: how you work together}

---

## Context and Collaboration

{2-3 sentences: shared projects, your role, frequency of interaction. This frames
everything below - a reader who doesn't know either of you should understand the
vantage point the feedback comes from.}

---

## Strengths and Contributions

{Grouped under 2-4 theme headings. Each bullet is a specific thing they did and the
impact it had. See "Section craft".}

### {Theme, e.g. Technical Leadership}
- **{Specific achievement}:** {a concrete instance - the named project/action - plus
  the impact / outcome. Not a general trait.}

### {Theme, e.g. Ownership and Accountability}
- **{Specific behavior}:** {what they actually did, on what, and how it helped the
  team/project}

---

## Growth and Development Opportunities

{Thin and positive - one or two sentences. A single forward-looking note that merges
growth and development: the next-level scope they're ready for, framed as a stretch and
a sign of belief in their trajectory, never a weakness or critique.}

---

## Overall Assessment

{2-4 sentences. Name their level and overall impact, then how that impact can be
deepened, and the upward trajectory; end on strong, unqualified support.}
```

The "Additional Notes" section is optional - include it only if there's relevant
context that doesn't fit elsewhere.

---

## Section craft

**Values** - tie at least one strength (and the growth note) to a named organizational
value, choosing the one the behavior genuinely demonstrates; leave the label off when none
fits. Take the value list from, in order: the user's request, a company-layer doc or skill
that supplies it, or the user when you ask during the interview. With no list available,
name the behavior itself (e.g. *candor*, *ownership*, *customer focus*) instead.

Across all sections, hold to these feedback guidelines: be constructive and
compassionate, name specific skills and behaviors, and keep it actionable - frame
growth as something to *continue* or *start*.

**Context** - Anchor it in real collaboration: which projects, your role, how often.
A good opener is "I have been working closely with {Name} on {project}…", signed by
the reviewer. This is the one place a little boilerplate is fine.

**Strengths** - The unit is a *concrete instance -> impact*, not a trait. Every bullet
must name a real thing she did - a specific project, action, or decision - and what
changed because of it. The test: could a reader who wasn't there picture the actual
event? "Strong engineer" and "great at coordination" fail it - they're traits with no
scene. "Led the pricing-engine redesign, cutting onboarding for a new pricing
rule from 2 weeks to 2 days via config" passes - it's an instance with an outcome.
When the notes hand you only a general trait, treat it as a prompt to dig for the
example, not as a sentence to polish. Group bullets under themes so a reader sees the
shape of the person:
- Technical Excellence / Technical Leadership
- Ownership and Accountability
- Collaboration and Communication
- Leadership and Mentorship (only if they actually did this)

Quantify whenever the notes support it (latency %, time saved, scope, # of pipelines,
incidents mitigated). Don't manufacture numbers - see Guardrails. Anchor at least one theme
to a value the behavior genuinely shows (e.g. catching upstream data bugs -> *candor*;
building reusable tooling others adopt -> *collaboration*).

**Growth and Development Opportunities** - One thin, positive section, one or two
sentences, answering *"how can they continue to grow and develop?"* Merge growth and
development into a single forward-looking note: the bigger scope they're ready for, tied
to a plausible next level or role (tech lead, design ownership, cross-team driver) and
to the value or skill it builds on. Keep it actionable - a *continue* or *start*, not a
vague wish. Frame it as a stretch and a sign of belief, never a weakness, gap, critique,
or personality judgment. If the notes give you nothing to point to, ask the user for the
next stretch they see - never manufacture a weakness.

**Overall Assessment** - A strong, positive endorsement answering *"what has been their
impact, and how can it be deepened?"* Name the level and the overall impact, then the
concrete path to deepen that impact, and the upward trajectory; end on clear, unqualified
support. Keep it forward-looking; this is the place to champion the person, not to hedge.

---

## DO / Guardrails

**DO**
- Use concrete examples; tie each to an outcome.
- Quantify impact when the notes support it.
- Lead with strengths and impact; keep growth thin, positive, and forward-looking.
- Make suggestions specific and doable within the next review period.
- Stay in the reviewer's voice; match the level of praise the notes actually justify.

**Guardrails**
- **Use only confirmed specifics.** This is a real document about a real person entering a real
  review. Never fabricate a project name, metric, or accomplishment that isn't in the
  notes or confirmed by the user. If a strength needs a number to land and you don't
  have one, ask - don't guess. A plausible-sounding invented metric is the single most
  damaging thing this skill could produce.

**Leave out**
- Personality judgments ("lazy", "difficult", "not a team player").
- Vague filler ("good job", "needs improvement", "great communicator").
- Comparisons to other teammates ("stronger than X", "unlike the rest of the team").
- Speculation about intentions or motivations.
- Feedback on things outside their control.
- Making it about you ("I would have done it differently").

---

## Phrase bank

Openers, for when a sentence won't start. Use sparingly - a specific example always
beats a stock phrase, and every opener here is only valid if a concrete instance
*immediately follows* it. "Demonstrated strong ownership by **walking ~20 pipelines to
surface missing event identifiers**" works; "Demonstrated strong ownership" alone is the
exact general-description failure this skill avoids. Treat "Consistently…" with extra
care - it invites a trait claim with no scene; only use it when you can list the
repeated, specific instances that make "consistently" true.

**Strengths:** "Demonstrated strong ownership by…" · "Delivered measurable impact
through…" · "Proactively identified and addressed…" · "Led the team through…"

**Growth:** "Could increase impact by…" · "Would benefit from…" · "An opportunity to
develop…" · "Going forward, consider…"

**Assessment:** "{Name} is a strong {level} engineer who…" · "Well-positioned to…" ·
"I strongly support {their} continued growth toward…"

---

## Worked example

This is the kind of transformation the skill exists for. The input is real working
notes - fragments, typos, project tags, no prose.

**Raw notes (input):**
```
[=] [Pricing engine]
  Delivered configurable pricing engine, tight timeline (2 weeks), PR1-PR9
  - Cut scope to core logic only due to timeline
  - Designed + documented validation strategy in a shared notebook (no existing
    pipeline to compare against)
  Reduced onboarding for a new pricing rule: 2 weeks -> 2 days via config
  Designed flexible billing window so customers see cost on arbitrary periods
[=] [Event platform integration]
  Walked ~20 offline pipelines to find required fields, uncovered gaps (missing
  event identifiers) - no dedicated time allotted for this
  Drove decision to move dedup + cross-account sharing to the event platform
```

**Finished output (Strengths section):**
```markdown
### Technical Leadership
- **Configurable Pricing Engine:** Designed and delivered the configurable pricing
  engine under a tight two-week timeline, making a deliberate scope cut to core logic
  to protect the deadline. With no existing pipeline to validate against, he designed
  and documented a step-by-step validation strategy in a shared notebook, giving the
  team confidence in correctness despite the lack of a baseline.
- **Extensibility by Design:** Built the engine so that adding a pricing rule dropped
  from a ~2-week effort to ~2 days through configuration, and designed a flexible
  billing window letting customers view cost over arbitrary periods.

### Ownership Beyond Scope
- **Event Platform Gap-Finding:** Without dedicated time allotted, walked through ~20
  offline pipelines to identify required fields, surfacing real gaps such as missing
  event identifiers before they became blockers. He drove the decision to move
  deduplication and cross-account sharing into the event platform, simplifying the
  downstream design.
```

Note what happened: fragments became full sentences; the impact already present in the
notes ("2 weeks -> 2 days", "~20 pipelines") was preserved exactly, not inflated;
project tags became theme headings; nothing was invented. The "no dedicated time"
detail was kept because it's what makes the ownership point land.
