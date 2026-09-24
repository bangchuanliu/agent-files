---
name: peer-feedback
kind: leaf
description: Turn rough notes about a colleague into a polished, LinkedIn/FAANG-standard peer-feedback document — Context, Strengths, a thin forward-looking Growth and Development note, Overall Assessment. Strength- and impact-led; interviews you for material gaps before writing, and never invents specifics. Use when - peer feedback, write peer feedback, feedback for a coworker, review a teammate (the person, not their PR), 360 feedback, calibration feedback, "help me write feedback for X", turn my notes into feedback, performance-review peer input, polish my feedback draft.
---

# Peer Feedback

Take rough, scattered notes about a colleague — bullet fragments, typos, a list of
shipped projects, or a thin first draft — and produce a finished peer-feedback
document in the standard structure. The hard part isn't the format; it's writing
*specific, impact-tied, behavior-focused* prose without inventing anything. That's
what this skill is for.

**Ground every strength in a real example, never a general trait.** A peer doc earns
its weight from concrete instances — a named project, a specific action, an observable
outcome — not from character descriptions. "She's great at coordination" is a trait and
says nothing; "she built and ran the tracker that split the platform into three streams
and landed it on time" is an example a reader can believe. Whenever you catch yourself
writing a general claim ("strong owner", "communicates well", "consistently delivers"),
stop and replace it with the specific thing she did. If the notes don't contain that
instance, ask for it — don't paper over the gap with a fluent generality.

**This is feedback about a real person entering a real review.** The cardinal rule:
never fabricate a project, metric, or accomplishment. When the notes are too thin to
write something true, ask — don't guess. Read `reference.md` (in this skill directory)
for the full template, section craft, DO/DON'T, and a worked example before writing.

**Always interview before writing.** Even when the notes look rich, pause and ask the
user your questions first, then wait for their answers before producing the document.
The user has more in their head than they wrote down — a launch outcome, the absolute
scale behind a percentage, the next stretch they see for this person — and surfacing it
is what turns a competent doc into one that actually lands in calibration. Don't write
the document on the first turn.

**This skill writes strong, positive endorsements.** Lead with impact and strengths,
and keep the single "Growth and Development" note thin and forward-looking — one stretch
framed as the next opportunity, never a weakness, deficiency, or critique. The goal is a doc that
champions the person. The one hard limit is honesty: positive does not mean invented —
every strength and number must be real (see the cardinal rule above).

**Follow LinkedIn's peer-feedback guidelines.** Be constructive and compassionate, cite
specific skills and behaviors (the example-first rule above), and keep it actionable —
frame growth as a clear *continue* or *start*, never a vague wish. Tie the content to
LinkedIn's six values and the three official prompts (the values list is in
`reference.md`):
- **Strengths → "How does this person demonstrate LinkedIn's values?"** Anchor at least
  one strength to a named LinkedIn value.
- **Growth and Development → "How can they continue to grow and develop?"** Name the
  value or skill the stretch builds on.
- **Overall Assessment → "What has been their impact, and how can it be deepened?"**
  State the impact, then the concrete path to deepen it.

Keep the whole document to **600 words or fewer.**

## Workflow

### 1. Gather the raw material
The user will point you at notes — a file path, pasted bullets, or prose. Read it.
Also establish four things; infer what you can, ask only for what's missing:
- **Name** of the colleague
- **Review period** (`YYYY-MM`) — LinkedIn cycles are typically May (`05`,
  mid-year) and December (`12`, annual). Infer from a filename like `yuan_2025_12`.
- **Reviewer** — default to the user (the existing docs use "Bangchuan Liu") unless
  told otherwise.
- **Working relationship** — one line; usually evident from the notes.

### 2. Map the notes onto the structure
Sort what you have into: context, strengths (and which theme each belongs to), and the
one forward-looking growth-and-development stretch. This shows you what's strong and
what's missing before you write a word.

### 3. Interview before writing — always, batched, lean
Present your questions and wait for the user's answers before writing the document.
Batch everything into one round so they answer once, and keep it tight — ask what
genuinely improves the feedback, not a checklist for its own sake. Group questions by
the section they feed.

**The interview's primary job is to collect the missing examples.** For every strength
the user gave you as a general claim — a trait, an adjective, a project name with no
scene — ask for the concrete instance behind it: what did she actually do, on what, and
what changed. Do not write a strength you couldn't get an example for; either get the
example or drop the point. Asking is the default, not a fallback.

The gaps worth asking about:
- **The forward-looking stretch.** Ask for the next bigger scope the user sees this
  person ready for — the one thing that becomes the thin "Growth and Development" note.
  Frame it as an opportunity, never a weakness or critique. Skip "what are they bad at"
  entirely; the question is "what's the next level they're ready to step into."
- **Any general claim — adjective or fluent sentence.** Not just "strong engineer" but
  also "she's great at coordination" or "consistently reliable" — these have no instance
  behind them. For each one, ask for the specific scene: what did she actually do, on
  what project, and what changed because of it. A general claim you can't anchor in an
  example shouldn't go in the doc.
- **Outcomes behind the work.** Even rich notes often stop at "delivered." Ask for the
  result that would turn a strength from "shipped X" into "shipped X, which did Y" —
  a launch metric, adoption, the absolute scale behind a percentage, a clean cutover.
- **Metrics you're unsure of**, and **review period / relationship** if you couldn't
  infer them.

If the user replies that they have nothing more to add, proceed — write the best
truthful doc from what you have. Distinguish two cases: a strength that has a real
instance but no number stays in, written qualitatively (never invent a figure); a
strength that is only a general trait with no instance behind it gets dropped, not
dressed up as prose.

### 4. Write the document (after the user has answered)
Follow the template in `reference.md` exactly. While writing, hold the line on:
- **Lead with impact and strengths.** Give the strengths the most space and the most
  specific, outcome-tied prose. Group them under 2-4 theme headings, **specific action
  → impact**, not adjectives.
- **One thin "Growth and Development" note.** Merge growth and development into a
  single one-or-two-sentence, forward-looking section — the next-level scope they're
  ready for, framed as an actionable *continue/start* (the value or skill it builds on).
  No weaknesses, no critique, no negatives.
- **Preserve the user's numbers exactly; add none of your own.** If the notes say
  "~20 pipelines" or "2 weeks → 2 days", keep it verbatim. If they don't give a
  number, write the qualitative truth instead of manufacturing one.
- **Strong, positive close that names impact and how to deepen it.** The Overall
  Assessment is an endorsement — name the level, the impact, the path to deepen that
  impact, and the upward trajectory; end on clear support.
- **Stay within 600 words** across the whole document. If you're over, tighten prose —
  never drop a concrete example to save words.

### 5. Save and report
Save as `{name}_{YYYY}_{MM}.md` (lowercase name). Default to the user's feedback folder,
`/Users/banliu/Documents/linkedin/peer-feedback/` (create it if missing); only save
elsewhere if the user names a different location. Then tell the
user, in one or two lines, anything you had to leave qualitative for lack of a number,
and any spot you'd strengthen with a concrete example if they have one — so they can
top it off before it goes into the review.

## Polishing an existing draft

If the user hands you a draft that's already in roughly the right shape, don't rewrite
it wholesale — tighten it against the same rules: convert vague praise to specifics,
compress growth into one thin forward-looking note, tie strengths to a LinkedIn value,
strip any personality judgments or peer comparisons, keep it within 600 words, and flag
(don't fill) places that need a real example.
