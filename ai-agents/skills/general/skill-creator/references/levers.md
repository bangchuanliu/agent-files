# Levers: definitions and rationale

Defines the italic terms in `SKILL.md`. Those rules are authoritative; this file explains them.

## Context pointers and loads

- **Context pointer:** an in-context reference that names out-of-context material and the condition for reaching it (a skill description, an `AGENTS.md` line naming a doc). Its _wording_, not its target, decides when and how reliably the agent reaches the material. A must-have target behind a weak pointer is a variance bug: sharpen the wording before inlining the material.
- **Branch:** a distinct case the document handles; different runs take different paths. A pointer lists the branches that should trigger it. Synonyms that rename one branch are one branch written twice.
- **Context load:** the cost of always-loaded material (descriptions, `AGENTS.md` lines) on the agent's window, paid every turn whether or not it fires. Prune pointers harder than bodies.
- **Cognitive load:** the cost on the human of remembering which documents exist and when to use each. Spend it where human judgement matters.

## Information hierarchy

Rank material by how immediately the agent needs it: in-file steps, then in-file reference, then disclosed reference behind a context pointer. **Progressive disclosure** moves material down the ladder: inline what every branch needs; disclose what only some branches reach. Push too little and the top bloats; push too much and needed material hides.

- **Co-location:** keep a concept's definition, rules, and caveats under one heading. (Scattering fragments one meaning; duplication repeats it.)
- **Sprawl:** a document too long even when every line is live and unique; attention thins. Cure it by disclosing reference and splitting by branch or sequence.

## Intent and unknowns

- **Intent:** the outcome a skill protects and why. Rules without intent are followed literally and fail on cases the author did not foresee; rules with intent generalize. This is why a guardrail document can replace a workflow: the agent plans its own steps toward a stated outcome inside stated limits.
- **Runtime unknown:** a fact the skill needs but cannot know when written (an input, a target, access, whether a check passed). Without a stated policy the agent either guesses silently, which fabricates, or stalls. Ask, a stated default, and stop-and-report are the three policies; irreversible or external actions only get ask or stop.

## Steps and completion criteria

- **Completion criterion:** the condition that tells the agent a step is done. Make it checkable (done vs not-done is clear) and demanding ("every modified model accounted for", not "produce a change list"); demand drives legwork, for flat reference as well as steps.
- **Unnecessary workflow:** a prescribed step order that protects no correctness, safety, recoverability, or external protocol. It overrides the agent's own planning for no gain; state the outcome instead.
- **Premature completion:** ending a step early because visible later steps pull attention toward being done. Sharpen the criterion first. Split the sequence only if the rush is observed, and only across a real context boundary (hand-off or subagent); an inline call clears nothing.

## Leading words and negation

- **Leading word:** a compact concept the model already knows from pretraining (_tight_ for "fast, deterministic, low-overhead"; _red_ for "a loop you believe in"). Repeated as a token, it anchors behaviour in the body and invocation in a pointer. Prefer an existing word; a coined one recruits no priors and must be defined.
- **Negation:** prohibition makes the forbidden behaviour more available. State the positive target. Keep a prohibition only as a hard guardrail that cannot be phrased positively, paired with the positive target.

## Pruning

- **Single source of truth:** one authoritative place per meaning, so changing a behaviour is a one-place edit. **Duplication** costs tokens and maintenance and inflates a meaning's prominence.
- **Environment:** config, scripts, directory layout, and `--help` are sources of truth. Restating them is a cache that goes stale; cache only expensive lookups and unwritten facts (conventions, reasons, gotchas).
- **Relevance:** delete lines that never bear on the task or have gone stale; otherwise they settle as sediment.
- **No-op:** an instruction the model already follows by default. The test is model-relative, so settle disputes by running the document. Delete the whole sentence. A leading word too weak to beat the default (_be thorough_) is a no-op; use a stronger word (_relentless_).
