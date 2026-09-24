# Vocab Capture & Sentence Rewrite

All operations for the user's personal dictionary at `~/personal/projects/skills/dict/data/`. Two operation families:

- **Op 1–5: Vocab** — save, look up, list, extract, and bulk-curate words/verbs.
- **Op 6: Sentence rewrite** — flag the user's own awkward sentences from the conversation and rewrite them as a native engineer would.

All persistent data is stored as **styled HTML tables**. Each file is a complete, self-contained HTML document — open in a browser to read.

Pick the operation whose Trigger line best matches the user's phrasing.

## File Layout

| File | Contains | Columns |
|------|----------|---------|
| `~/personal/projects/skills/dict/data/dict.html` | General words, phrases, idioms (active learning) | Word / Phrase · Meaning · Synonyms · Example · **Progress** |
| `~/personal/projects/skills/dict/data/tech-verb.html` | Verbs (active learning) | Verb · Meaning · Synonyms · Example · **Progress** |
| `~/personal/projects/skills/dict/data/sentence-fixes.html` | Sentence rewrites from Op 6 (active learning) | Your sentence · Native rewrite · Style notes · **Progress** |
| `~/personal/projects/skills/dict/data/history.html` | Graduated entries (`●●●●●` reached) — verbs / words / sentences in three sections | Same as source + `Graduated` date |
| `~/personal/projects/skills/dict/data/<name>.html` | User-named files (e.g., `legal.html`) | Same vocab schema |

## Vocab Row Format (Ops 1, 4, 5)

Append a `<tr>` row to the `<tbody>` of the target HTML file:

```html
<tr>
  <td class="col-word">WORD <span class="count">×N</span></td>
  <td class="col-meaning">MEANING</td>
  <td class="col-syn">SYNONYM_1, SYNONYM_2</td>
  <td class="col-example">"EXAMPLE_SENTENCE"</td>
  <td class="col-progress"><span class="filled"></span><span class="empty">○○○○○</span></td>
</tr>
```

- **Synonyms are required** (1–2), everyday-register. If no true synonym exists, use `<td class="col-syn empty">—</td>`.
- **Count badge** (`<span class="count">×N</span>`) appears only when N ≥ 2. Omit it for first occurrences.
- **Progress cell** always starts as `<span class="filled"></span><span class="empty">○○○○○</span>` (0 filled, 5 empty). It's updated by Op 7.
- HTML-escape `<`, `>`, `&` in user content.
- Example sentences stay in straight ASCII quotes (`"…"`); the column CSS renders them italic.

## Universal Rules

- **Sweep before append.** Before adding any new entry to an active HTML file, scan that file's `<tbody>` for rows whose progress cell is `<span class="filled">●●●●●</span><span class="empty"></span>` (5 dots). Move each such row into the matching section of `history.html` — strip the `<td class="col-progress">…</td>` cell and insert a `<td class="col-graduated">YYYY-MM-DD</td>` cell with today's date. **Preserve the count badge (`<span class="count">×N</span>`) on the col-word / col-orig cell when graduating** — history rows track recurrence the same way active rows do. Do the sweep first, then the **history check**, then the **active-file dedupe check**, then the append.
- **History check FIRST.** Before scanning the active file, scan the matching section of `history.html` (verb section for `tech-verb.html`, dict section for `dict.html`, sentence section for `sentence-fixes.html`) for an existing row with the same word/sentence (case-insensitive, trimmed). **If found in history → increment the count badge on the history row and STOP. Do not touch the active file.** The user has already graduated this entry; surfacing it again just bumps recurrence on the graduated record so the user sees how often it keeps coming up. Report e.g. `"backfill" already graduated — bumped to ×3 in history.html`.
- **Active-file check before append.** Only reached when the history check finds no match. Scan the target active HTML for an existing row with the same word (case-insensitive, trimmed). If found, increment the count badge on the existing active row. If not found, append a new row with an empty progress cell.
- **Append** new `<tr>` rows just before the closing `</tbody>` tag — never overwrite the file unless the user explicitly asks for a rebuild.
- If the target HTML file doesn't exist, create it from scratch using the scaffold/CSS in the existing files at `~/personal/projects/skills/dict/data/` as the template.
- Use the Python helper below (or equivalent) to atomically handle both the check-and-increment and the append paths; avoid `echo`/`printf` for HTML edits since they can mis-place rows relative to `</tbody>`.
- One `<tr>` per unique entry. No line breaks inside `<td>` cells unless using `<ul>`/`<li>` (Op 6 only).
- Trim leading/trailing whitespace from the word before saving and matching.
- After the operation, report to the user whether you **added a new row** or **incremented a count** (e.g., "wire up ×4 (count incremented)" vs. "added new row: backfill").
- **Always print the touched file paths at the end of the response** so the user can open them from the terminal. Show only the files actually read or written. Format:
  ```
  ~/personal/projects/skills/dict/data/tech-verb.html
  ~/personal/projects/skills/dict/data/dict.html
  ```
- **50-row guardrail.** After every add/increment in `dict.html`, `tech-verb.html`, or `sentence-fixes.html`, count the active (non-graduated) rows in the file's `<tbody>`. If the count is ≥ 50, surface a warning in your response: `⚠️ {filename} now has {N} active rows — you're accumulating, not learning. Time to review and bump progress on the highest-frequency entries.` Repeat the warning on every operation until the count drops below 50 (via graduation to `history.html`).

### Insert helper (reuse across Ops 1, 4, 5)

The helper enforces the three-step rule: **history check → active-file dedupe check → append**. `col_class` is `col-word` for verbs/dict and `col-orig` for sentences. `history_section` keys the history-side scan to the right section anchor (history.html has three independent sections in one file).

```bash
python3 - <<'PY'
import re
from pathlib import Path

# --- inputs ---
file_path = Path.home() / "personal/projects/skills/dict/data/dict.html"   # change per call
word      = "WORD"
meaning   = "MEANING"
syns      = "SYN1, SYN2"   # use "" for no synonyms
example   = "EXAMPLE"
# ---

HIST = Path.home() / "personal/projects/skills/dict/data/history.html"
HIST_SECTION_BY_FILE = {
    "tech-verb.html":      "<!-- Append <tr> rows here when a verb",
    "dict.html":           "<!-- Append <tr> rows here when a word",
    "sentence-fixes.html": "<!-- Append <tr> rows here when a sentence",
}
COL_CLASS = "col-orig" if file_path.name == "sentence-fixes.html" else "col-word"
word_lc   = word.strip().lower()

# A row's col-{word|orig} cell, with an optional count badge.
row_cell_re = re.compile(
    rf'(<td class="{COL_CLASS}">)([^<]+?)(\s*<span class="count">×(\d+)</span>)?(</td>)',
    re.IGNORECASE,
)

def bump_in(text, target_lc):
    """Return (new_text, bumped:bool, new_count:int|None). Increments first match only."""
    bumped = {"hit": False, "n": None}
    def repl(m):
        if bumped["hit"]:
            return m.group(0)
        if m.group(2).strip().lower() != target_lc:
            return m.group(0)
        current = int(m.group(4)) if m.group(4) else 1
        new_n   = current + 1
        bumped["hit"] = True
        bumped["n"]   = new_n
        return f'{m.group(1)}{m.group(2).rstrip()} <span class="count">×{new_n}</span>{m.group(5)}'
    new_text = row_cell_re.sub(repl, text)
    return new_text, bumped["hit"], bumped["n"]

# ── Step 1: history check (only the section matching this file) ──
hist_text = HIST.read_text()
section_anchor = HIST_SECTION_BY_FILE[file_path.name]
# Slice history.html into [before_section, section_body, after_section] so we only bump within the right section.
anchor_pos = hist_text.find(section_anchor)
if anchor_pos != -1:
    # Section body = from the previous <tbody> opener to this anchor comment.
    tbody_open = hist_text.rfind("<tbody>", 0, anchor_pos)
    if tbody_open != -1:
        before, section, after = hist_text[:tbody_open], hist_text[tbody_open:anchor_pos], hist_text[anchor_pos:]
        new_section, hit, n = bump_in(section, word_lc)
        if hit:
            HIST.write_text(before + new_section + after)
            print(f'already graduated — bumped to ×{n} in history.html: {word}')
            raise SystemExit(0)

# ── Step 2: active-file dedupe check ──
text = file_path.read_text()
new_text, hit, n = bump_in(text, word_lc)
if hit:
    file_path.write_text(new_text)
    print(f"incremented to ×{n}: {word}")
    raise SystemExit(0)

# ── Step 3: append a new row ──
syn_cell = f'<td class="col-syn">{syns}</td>' if syns.strip() else '<td class="col-syn empty">—</td>'
row = (f'      <tr><td class="{COL_CLASS}">{word}</td>'
       f'<td class="col-meaning">{meaning}</td>'
       f'{syn_cell}'
       f'<td class="col-example">"{example}"</td>'
       f'<td class="col-progress"><span class="filled"></span><span class="empty">○○○○○</span></td></tr>')
file_path.write_text(text.replace('    </tbody>', row + '\n    </tbody>'))
print(f"added new row: {word}")
PY
```

---

## Operation 1 — Add a single entry

**Trigger:** "save word X", "add X to vocab", "save baked into", "add this to dict.html".

Route by entry type:
- Verbs (including phrasal verbs) → `~/personal/projects/skills/dict/data/tech-verb.html`
- Everything else (nouns, adjectives, idioms, phrases) → `~/personal/projects/skills/dict/data/dict.html`
- User-named files → `~/personal/projects/skills/dict/data/<name>.html`

Use the insert helper above with the chosen file path and row content.

## Operation 2 — Look up

**Trigger:** "look up X", "define X", "do I have X saved".

```bash
grep -oE 'class="col-word">[^<]*</td><td class="col-meaning">[^<]*' ~/personal/projects/skills/dict/data/*.html \
  | grep -i 'WORD'
```

Search both `dict.html` and `tech-verb.html` if the user doesn't specify a file. Open the file in a browser for full context: `open ~/personal/projects/skills/dict/data/dict.html`.

## Operation 3 — List

**Trigger:** "list my vocab", "list all words", "show dict".

```bash
# All words from both files, alphabetical:
grep -oE 'class="col-word">[^<]*' ~/personal/projects/skills/dict/data/{dict,tech-verb}.html \
  | sed 's/.*">//' | sort -u
```

For visual browsing: `open ~/personal/projects/skills/dict/data/dict.html` (and `tech-verb.html`).

---

## Operation 4 — Sentence Vocab Extractor

**Trigger:** user provides an example sentence (or short passage) and asks to extract/save/harvest vocab.

**Behavior:** split into two buckets and append `<tr>` rows to two HTML files.

| Bucket | File |
|--------|------|
| Verbs (action words, phrasal verbs) | `tech-verb.html` |
| Other valuable words (nouns, adjectives, idioms, phrases) | `dict.html` |

### Selection Rules

- Skip filler words: articles, common prepositions, auxiliaries (`is`, `was`, `the`, `of`, etc.).
- **Capture liberally — exposure beats curation.** Default toward including a candidate when in doubt. The history-check dedup (see Universal Rules) absorbs accidental repeats, so over-capture is cheap; under-capture costs a learning opportunity. Aim for **5–10 entries** from a typical sentence and **10–20** from a multi-sentence passage, split across `tech-verb.html` and `dict.html`.
- **Cover every content-bearing word at least once.** For each clause, harvest: (a) the main verb, (b) every noun phrase that names a concept (artifact, role, metric, state), (c) every adjective that carries weight (severity, scope, certainty), (d) every adverbial idiom (`out of the blue`, `by design`, `on purpose`). When you can choose between a generic word and a more specific one in the source, save both as separate entries.
- **Prioritize negative-prefix verbs and phrasal verbs** — high-signal because the user defaults to "not + verb" or generic single-word equivalents. When the source uses a generic verb or "not + verb" pattern, **also surface the prefix/phrasal alternative** as an additional entry, even if the source didn't use it. Examples:
  - Negative-prefix verbs (`mis-`, `dis-`, `un-`, `over-`, `under-`, `out-`, `re-`, `mal-`): `disagree` (vs. "not agree"), `misread` (vs. "read wrong"), `overlook` (vs. "not notice"), `underestimate` (vs. "not expect enough"), `unblock` (vs. "remove blocker"), `dismiss` (vs. "not consider"), `override` (vs. "force ignore"), `outpace` (vs. "go faster than").
  - Phrasal verbs (verb + particle): `push back` (vs. "disagree strongly"), `drill down` (vs. "look at in detail"), `loop in` (vs. "include someone"), `take offline` (vs. "discuss later"), `circle back` (vs. "revisit"), `pull in` (vs. "request help from").
- Inclusion standard — every entry must pass these three (a single low-confidence "maybe" still gets included; previously rejected by criterion 4, now allowed):
  1. **Real, current English** — a native speaker would actually use it in tech work; not a coinage, archaism, or jargon-only term.
  2. **Idiomatic in pro contexts** — would plausibly appear in a Slack thread, PR comment, or design doc.
  3. **Reusable** — works across multiple situations, not just the source sentence.
  (Redundancy with a more common synonym is no longer a rejection criterion — save both and let the user pick which one feels right when graduating.)
- Lemmatize verbs to base form (`shipped` → `ship`, `pushing back` → `push back`).
- **Examples must be NEW**, not the original sentence. Write a fresh, ≤10-word, native-speaker-idiomatic example for each entry.

### Output to the User

After appending:
1. List the entries you added, grouped by file (plain text in chat — `verb · meaning · syn · example`). Don't echo the raw HTML.
2. List candidate words you **considered but skipped** as low-signal (generic verbs like *provide, ask, require*; generic modifiers like *future, minor, new*). One short line, no examples.

### Example

> **Input:** *"We need to circle back on the rollout strategy because the initial telemetry surfaced a regression."*
>
> **Appended to `tech-verb.html`:**
> - circle back · revisit a topic later · follow up, revisit · "Let's circle back after the demo."
> - surface · bring an issue into visibility · reveal, expose · "The dashboard surfaced a latency spike."
>
> **Appended to `dict.html`:**
> - rollout strategy · the plan for releasing a change · launch plan, release plan · "The rollout strategy needs sign-off."
> - telemetry · runtime metrics from production · monitoring data, observability · "Telemetry caught the regression first."
> - regression · a previously-fixed bug returning · relapse, backslide · "The deploy introduced a regression."
>
> **Skipped as low-signal:** *need, initial, because* — too generic.

---

## Operation 5 — Bulk Tech Verb Curation

**Trigger:** "extract tech verbs", "generate 500 verbs", "curate tech vocab".

Act as a **Senior Communication Coach for the Tech Industry (Silicon Valley style)**. Help the user master high-frequency verbs used in daily professional tech interactions. Provide **500 verbs** by default unless the user specifies a different count.

### Verb Categories

Group verbs into these 5 daily scenarios. Since the HTML schema has no Category column, encode the category as a parenthetical suffix on the meaning, e.g., `revisit a topic later (meetings)`.

1. 🗓️ **Meetings & Syncs** — status updates, coordination
2. ⚔️ **Debates & Decision Making** — strategy, disagreement, proposing ideas
3. 🎤 **Presentations & Demos** — explaining concepts, guiding an audience
4. ☕ **Small Talk & Socializing** — lunch, coffee chats, networking
5. 💻 **Technical Execution** — coding, devops, specific work actions

### Selection Criteria

Prioritize **two categories the user commonly misses**, in this order:

1. **Phrasal verbs** (verb + particle) — idiomatic in pro speech: *circle back, push back, drill down, loop in, take offline, pull in, ship it, dog-food, level-set, double-click, hash out, lock in, spin up, tee up, kick off, wind down, sign off, walk back, knock out, sort out*.
2. **Negative-prefix verbs** (`mis-`, `dis-`, `un-`, `over-`, `under-`, `out-`, `re-`, `mal-`) — replace clunky "not + verb": *misread, misjudge, misalign, disagree, dismiss, disregard, unblock, undo, undercut, overlook, override, overrule, overstate, underestimate, outpace, outperform, outscope, rewrite, revisit, refactor*.

Then other "insider" terms: *flag, table, align, socialize (an idea), hard-stop, rubber-stamp, spike, red-line, green-light*.

Aim for **~40% phrasal verbs and ~30% negative-prefix verbs** in the output to address the user's stated gap.

### Output

Append `<tr>` rows to `~/personal/projects/skills/dict/data/tech-verb.html`. Standard vocab schema (Verb · Meaning · Synonyms · Example). Encode scenario category as a `(meetings)`, `(debates)`, etc. suffix on the meaning.

### Tone

Professional, concise, idiomatic. Examples must be practical and immediately usable.

---

## Operation 6 — Authentic Sentence Rewrite

**Trigger:** "flag issues in my sentences", "rewrite my sentences", "scan the conversation for awkward sentences", "fix sentences in this thread", "review my sentences".

**Philosophy — read before writing.** This is **not** a grammar checker. For each flagged sentence, produce the rewrite a senior native engineer would actually write in Slack, a PR comment, or a 1:1 IM — after fully understanding the user's intent. The user is past the rule-level stage; their gap is **idiom, register, and restructuring**, so every style note calls out that gap explicitly.

### Process

1. **Understand intent.** Re-read in conversation context. What is the user trying to communicate, to whom, in what register (Slack, PR, agent IM)?
2. **Filter — flag generously.** Only skip true throwaways: single-word affirmations (`yes`, `ok`, `thanks`), command snippets (`gh pr view`), and code/file references. Flag any sentence where a native engineer would phrase it noticeably differently — including pure stylistic upgrades that don't change meaning, mild article/preposition drift, or sentences that are technically fine but would read flat in Slack. **When in doubt, flag it** — the history-check dedup absorbs repeats, and surfacing more sentences gives the user wider exposure to the native-rewrite patterns.
3. **Rewrite, don't patch.** Restructure freely: drop redundancy, use phrasal/negative-prefix verbs, adopt dev-IM register cues (`FYI`, `Heads up`, `Out of curiosity`, `Quick question`), shorten paths/quoted strings when context makes them obvious. Calibrate by severity — worse sentences earn larger rewrites.
4. **Style notes — ≤3 bullets.** Each bullet calls out one idiom/register/restructuring upgrade and *why* an engineer would phrase it that way. Do **not** explain grammar rules.

### Output

Append a `<tr>` row to `~/personal/projects/skills/dict/data/sentence-fixes.html` (three columns: **Your sentence · Native rewrite · Style notes**).

**Row template:**

```html
<tr>
  <td class="col-orig">ORIGINAL_SENTENCE <span class="count">×N</span></td>
  <td class="col-native">NATIVE_REWRITE</td>
  <td class="col-notes"><ul>
    <li>BULLET_1</li>
    <li>BULLET_2</li>
    <li>BULLET_3</li>
  </ul></td>
  <td class="col-progress"><span class="filled"></span><span class="empty">○○○○○</span></td>
</tr>
```

- **Max 3 bullets** in `col-notes`; minimum 1.
- Each bullet is one short, parallel sentence — focus on one upgrade per bullet.
- Use em dashes (`—`) inside cell text for clarity.
- Wrap inline code/paths in `<code>…</code>` when they look code-like.
- **Count badge** (`<span class="count">×N</span>`) appears only when N ≥ 2; omit for first occurrences.

### Check before append (Op 6)

Apply the same three-step rule as vocab: **history-first, then active, then append**.

1. **History check (sentence section of `history.html`)** — scan only the sentence-section `<tbody>` (the one anchored by `<!-- Append <tr> rows here when a sentence`). Match on:
   - **Exact sentence match** (whitespace-normalized, case-insensitive) → bump count badge on the col-orig cell in history and STOP. Report e.g. `already graduated — bumped to ×3 in history.html`.
   - **Issue-pattern match** — if the existing graduated row's bullets cover the same idiom/register gap (≥2 of 3 bullets address the same upgrade), treat as repeat → bump and STOP.
2. **Active-file dedupe (`sentence-fixes.html`)** — if no history match, scan the active file the same way. Found → increment the active count badge.
3. **Append** — if neither check fires, append a new row to `sentence-fixes.html`.

When incrementing (history or active), report the matched original sentence and the new count (e.g., `"…subject drop after 'so'…" ×3 (count incremented in history.html)`). Do not modify the existing rewrite or bullets — the count reflects how often this *type* of issue has recurred.

### Example Row

> **Input:** *"dict skill disappear after removing the symlink"*
>
> **Appended row:**
> ```html
> <tr>
>   <td class="col-orig">dict skill disappear after removing the symlink</td>
>   <td class="col-native">Heads up — dict's gone from the skill list after that rm.</td>
>   <td class="col-notes"><ul>
>     <li>Engineers open unexpected findings with "Heads up" or "FYI".</li>
>     <li>"Gone from the skill list" is concrete vs. abstract "disappeared".</li>
>     <li>"That rm" is dev-IM shorthand for the command just run.</li>
>   </ul></td>
>   <td class="col-progress"><span class="filled"></span><span class="empty">○○○○○</span></td>
> </tr>
> ```

---

## Operation 7 — Update Learning Progress

**Trigger:** "I used X today", "progress X +1", "mark X learned", "bump X", "graduate X", "review my progress", "show progress".

Tracks how well the user actually owns each entry. The Progress column shows 5 dots: each filled dot represents a milestone in the journey from *encountered* → *owned*.

### Progress Milestones

| Dots | Milestone |
|------|-----------|
| `○○○○○` | Just added — encountered for the first time. |
| `●○○○○` | Re-encountered in reading/listening and recognized it. |
| `●●○○○` | Used it in a real Slack message, PR comment, or design doc. |
| `●●●○○` | Used it unprompted in a live conversation or meeting. |
| `●●●●○` | Explained it to someone else in your own words. |
| `●●●●●` | You own it — **stays in place** until the next entry is added to this file, at which point the row sweeps into `history.html`. The dropdown does not graduate on its own. |

### Update Actions

| User says | Effect |
|-----------|--------|
| "I used `<word>` today" / "bump `<word>`" | +1 filled dot on the matching row |
| "progress `<word>` +N" | +N filled dots (capped at 5) |
| "graduate `<word>`" | Force-move the row to `history.html` regardless of current dot count |
| "review my progress" / "show progress" | Print a summary: rows grouped by progress level, counts per group |
| "demote `<word>`" / "progress `<word>` -1" | -1 filled dot (rare, but supported) |

### Process

1. **Identify the file.** Match by word/sentence in `dict.html` first, then `tech-verb.html`, then `sentence-fixes.html`. If ambiguous, ask the user.
2. **Locate the row** by case-insensitive match on the col-word / col-orig cell.
3. **Update the dots** in the `col-progress` cell: `filled` span gets N `●` characters, `empty` span gets `5 - N` `○` characters. **Reaching 5 does not auto-graduate** — the row stays in place and shows `●●●●●`. Graduation happens lazily, as a sweep before the next Op 1/4/5 append (see Universal Rules → "Sweep before append").
4. **Force-graduate (`graduate <word>`):** Skip the sweep deferral and immediately run the graduation routine on the matched row — remove from source, append to the matching section of `history.html` with today's date in `col-graduated`.
5. **Report** the new state, e.g., `wire up: ●●●○○ → ●●●●○ (used unprompted ✓)`, `wire up: ●●●●○ → ●●●●● (ready to graduate on next add)`, or for force-graduate: `wire up: ●●●●● → graduated to history.html on 2026-05-15 🎓`.

### Update Helper

Use **`bump_progress`** to change the dot count (no graduation — even at 5, the row stays put). Use **`graduate_one`** for force-graduate. Use **`sweep_graduated`** to run the pre-append sweep that moves all `●●●●●` rows in a file into `history.html`.

```python
# Reusable helper — paste at the top of the script for any of the three actions below.
import re
from datetime import date
from pathlib import Path

DICT = Path.home() / "personal/projects/skills/dict/data"
HIST = DICT / "history.html"
SECTION_ANCHOR = {
    "tech-verb.html":      "<!-- Append <tr> rows here when a verb",
    "dict.html":           "<!-- Append <tr> rows here when a word",
    "sentence-fixes.html": "<!-- Append <tr> rows here when a sentence",
}
FILLED_RE = re.compile(r'<span class="filled">(●*)</span><span class="empty">(○*)</span>')

def col_class(file_name):
    return "col-orig" if file_name == "sentence-fixes.html" else "col-word"

def find_row(text, file_name, needle):
    cell_re = re.compile(
        rf'class="{col_class(file_name)}">([^<]+?)(\s*<span class="count">.*?</span>)?</td>',
        re.IGNORECASE,
    )
    needle = needle.strip().lower()
    for m in re.finditer(r"\s*<tr>(.*?)</tr>", text, re.DOTALL):
        cm = cell_re.search(m.group(1))
        if cm and cm.group(1).strip().lower() == needle:
            return m
    return None

def move_to_history(file_name, row_html):
    """Append a row to history.html (replacing col-progress with col-graduated date)."""
    row_html = re.sub(
        r'<td class="col-progress">.*?</td>',
        f'<td class="col-graduated">{date.today().isoformat()}</td>',
        row_html, flags=re.DOTALL,
    )
    htext = HIST.read_text()
    htext = htext.replace(SECTION_ANCHOR[file_name], row_html.strip() + "\n      " + SECTION_ANCHOR[file_name])
    HIST.write_text(htext)

# ─── Action 1: bump progress (no graduation at 5) ───
def bump_progress(file_name, word_or_sentence, delta):
    src = DICT / file_name
    text = src.read_text()
    m = find_row(text, file_name, word_or_sentence)
    if not m:
        return f"not found: {word_or_sentence}"
    fm = FILLED_RE.search(m.group(1))
    current = len(fm.group(1)) if fm else 0
    new_count = max(0, min(5, current + delta))
    new_progress = f'<span class="filled">{"●" * new_count}</span><span class="empty">{"○" * (5 - new_count)}</span>'
    new_body = FILLED_RE.sub(new_progress, m.group(1), count=1)
    src.write_text(text[:m.start(1)] + new_body + text[m.end(1):])
    tail = " (ready to graduate on next add)" if new_count == 5 else ""
    return f"{word_or_sentence}: {'●'*current}{'○'*(5-current)} → {'●'*new_count}{'○'*(5-new_count)}{tail}"

# ─── Action 2: force-graduate a single row ───
def graduate_one(file_name, word_or_sentence):
    src = DICT / file_name
    text = src.read_text()
    m = find_row(text, file_name, word_or_sentence)
    if not m:
        return f"not found: {word_or_sentence}"
    move_to_history(file_name, m.group(0))
    src.write_text(text[:m.start()] + text[m.end():])
    return f"{word_or_sentence}: graduated to history.html on {date.today().isoformat()} 🎓"

# ─── Action 3: sweep all ●●●●● rows in a file (run before Op 1/4/5 append) ───
def sweep_graduated(file_name):
    src = DICT / file_name
    text = src.read_text()
    moved = []
    five_re = re.compile(
        r'\s*<tr>(?:(?!</tr>).)*?<span class="filled">●●●●●</span><span class="empty"></span>(?:(?!</tr>).)*?</tr>',
        re.DOTALL,
    )
    matches = list(five_re.finditer(text))
    for m in reversed(matches):  # reversed so offsets stay valid as we splice
        cell_re = re.compile(
            rf'class="{col_class(file_name)}">([^<]+?)(\s*<span class="count">.*?</span>)?</td>',
            re.IGNORECASE,
        )
        cm = cell_re.search(m.group(0))
        if cm:
            moved.append(cm.group(1).strip())
        move_to_history(file_name, m.group(0))
        text = text[:m.start()] + text[m.end():]
    src.write_text(text)
    return moved  # list of items graduated, or [] if nothing to sweep
```

**Usage examples:**

```python
print(bump_progress("tech-verb.html", "wire up", +1))
print(graduate_one("dict.html", "code smell"))
moved = sweep_graduated("tech-verb.html"); print(f"swept: {moved}")
```

### Review Progress Action

When the user says *"review my progress"* / *"show progress"*, parse all three active files and print a summary:

```
tech-verb.html — 29 active
  ○○○○○ : 24
  ●○○○○ : 3
  ●●○○○ : 1
  ●●●○○ : 1
  ●●●●○ : 0
  ●●●●● : 0 (graduations happen automatically)

dict.html — 36 active
  …
sentence-fixes.html — 16 active
  …

history.html — N graduated total
```

This makes the "accumulation vs. learning" gap visible at a glance.

---

## Browser-Based Progress Editing (Local Server)

The HTML files include an embedded dropdown UI that lets the user update progress dots **directly in the browser**, with edits saved to disk via a separate `local-server` skill. The server itself lives at `~/personal/projects/skills/local-server/server.py` and is reusable by any personal-data skill — dict just points it at `~/personal/projects/skills/dict/data/`.

### Starting the server

```bash
python3 ~/personal/projects/skills/local-server/server.py --dir ~/personal/projects/skills/dict/data --port 8765
```

(`--dir` is required for dict — the generic server defaults to `~/personal/dict`, not the dict data dir.)

Prints:

```
Serving ~/personal/projects/skills/dict/data on http://localhost:8765/
  ➜  http://localhost:8765/dict.html
  ➜  http://localhost:8765/history.html
  ➜  http://localhost:8765/sentence-fixes.html
  ➜  http://localhost:8765/tech-verb.html
```

Open any URL. The Progress column renders as a dropdown styled to look like dots; selecting a value triggers `POST /update-progress`, which mutates the file on disk. A toast confirms the save. Selecting `●●●●● 🎓` graduates the row (server moves it to `history.html` with today's date, browser fades it out).

### How the JS knows whether the server is running

The embedded script only activates on `http://` or `https://`. If the user opens the file via `file://` (e.g., from Finder), the dropdown UI no-ops and the static dots stay visible — read-only mode.

### Endpoint

`POST /update-progress` with JSON body:

```json
{
  "file": "tech-verb.html",
  "item": "wire up",
  "progress": 3
}
```

Server returns `{"status": "ok", "message": "wire up: 3/5"}` on success or `{"status": "error", "message": "<reason>"}` on failure.

### Op 7 vs. browser UI

Both paths target the same on-disk format and graduation flow — use whichever is faster:
- **Browser dropdown** — best for casual one-off bumps during a review session.
- **Op 7 via Claude** — best for batch updates ("bump all phrasal verbs +1"), force-graduate, or when the server isn't running.

---

## Operation 8 — Preview (Start Local Server)

**Trigger:** "preview", "open dict in browser", "browse dict", "start dict server", "start server", "/dict preview".

Delegates to the `local-server` skill (see `~/personal/projects/skills/local-server/`). Idempotently starts the server pointed at `~/personal/projects/skills/dict/data/` and prints the URLs.

### Process

1. **Check if a server is already listening on port 8765**:
   ```bash
   lsof -nP -iTCP:8765 -sTCP:LISTEN 2>/dev/null
   ```
   - If output is non-empty, the server is already running. Skip to step 3.
2. **Start the server detached** so it survives the current Claude session:
   ```bash
   nohup python3 ~/personal/projects/skills/local-server/server.py --dir ~/personal/projects/skills/dict/data --port 8765 \
     > /tmp/dict-server.log 2>&1 &
   disown
   ```
   Then wait until the port is reachable:
   ```bash
   for i in 1 2 3 4 5; do
     curl -s -o /dev/null http://localhost:8765/tech-verb.html && break
     sleep 0.2
   done
   ```
3. **Print the URLs** in your response so the user can click any of them in the terminal:
   ```
   Dict server is running on http://localhost:8765/

     ➜  http://localhost:8765/tech-verb.html       (29 active)
     ➜  http://localhost:8765/dict.html            (36 active)
     ➜  http://localhost:8765/sentence-fixes.html  (16 active)
     ➜  http://localhost:8765/history.html         (graduated entries)

   Stop with "/dict stop server" or `pkill -f personal/projects/skills/local-server/server.py`.
   ```
   Replace the active counts with the live values from each file (`grep -c '<td class="col-word"' tech-verb.html` etc.).
4. **Do not auto-open the browser** — let the user click the link they want.

### Edge cases

- If `python3` isn't on PATH, the start command fails silently; check the log at `/tmp/dict-server.log` and report the error.
- If port 8765 is bound by something *other* than the local-server process, report the conflict and suggest the user kill that process or pass `--port` to use a different port.

---

## Operation 9 — Stop Server

**Trigger:** "stop server", "stop dict server", "kill dict server", "/dict stop".

Kill the background server process:

```bash
pkill -f "personal/projects/skills/local-server/server.py" \
  && echo "local server stopped" \
  || echo "no local server was running"
```

Report the outcome. If the server wasn't running, that's a no-op — say so plainly. Note: this kills **all** local-server instances regardless of port; if you have multiple data skills using their own ports, prefer `lsof -nP -iTCP:8765 -sTCP:LISTEN -t | xargs -r kill` for surgical stops.
