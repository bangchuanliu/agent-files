---
name: slack-msg
kind: leaf
description: "Rewrite or draft a short, polite message you're about to SEND to a coworker on Slack/IM/DM (or similar chat). Goal: ship a clear, professional outgoing message. Use when: slack message, IM, DM, message a coworker, draft a message to send, 'make this message more polite/concise', 'reword this before I send it', reply to a thread. NOT for improving your own English as a learner or polishing an AI-agent prompt — use dict for those."
---

# Slack Message Writer

Rewrite or generate Slack messages that are polite, professional, and clear.

## Priority Order

When rules conflict, apply in this order:
1. **Correct & clear meaning** — fix weak collocations and ambiguous phrasing first; a polite sentence that says the wrong thing is worse than a blunt one that's right
2. **Polite tone** — never abrupt, never passive-aggressive
3. **Professional** — appropriate register for a work context
4. **Concise** — no filler, no redundancy
5. Everything else (formatting, structure)

## Rules

0. **Fix unclear or non-native phrasing** — don't just preserve the draft's wording. Correct it so the meaning is right and natural:
   - **Weak collocations** — replace verbs/nouns that don't pair naturally with the idiomatic choice. E.g. "extract the complexity" → "factor out the complexity"; "do a decision" → "make a decision". You don't *extract* complexity; you *isolate*, *factor out*, or *reduce* it.
   - **Ambiguous meaning** — if a phrase has two readings, pick the most likely one for the context, rewrite so only that reading survives, and add a one-line note to the user stating the assumption (this is the one allowed exception to "no clarifying questions" — assume, don't block).
   - **Articles & grammar** — add missing `the`/`a`, fix agreement, drop stray hyphens (e.g. "attribution-level complexity" → "attribution complexity" when no level/tier is meant).
   - Preserve the user's intent and technical terms; change only the wording that's wrong or unclear.
1. **Lead with the point** — ask or update first, context second
2. **Be polite, not verbose** — one "thanks" or "please" is enough, no filler
3. **Short sentences** — break compound sentences, remove qualifiers
4. **Bullet points** for 2+ items — always start at column 0, never indent
5. **No indentation** — all lines at column 0, Slack messages must be flat
6. **Slack formatting** — `*bold*`, backticks for code, `>` for quotes, `<url|text>` for links
7. **Match tone** — peers: direct; leadership: outcome-focused; cross-team: add context
8. **Clear next step** if action needed — "Could you review by Friday?" not "Let me know"
9. **Tables → code blocks** — Slack doesn't render markdown tables; use monospaced code blocks with aligned columns and emoji status icons

## Slack-Native Formatting

Bold: `*bold*` | Italic: `_italic_` | Strike: `~text~` | Code: backticks | Links: `<url|text>` | Lists: `- ` or `•` | Headings: use `*Bold text*` on own line | Tables: code blocks only

**Do NOT use**: `**bold**`, `# headings`, `[text](url)`, markdown tables with `|---|`

## Output

`SKILL_DIR` = the directory containing this file.

Always write to `$SKILL_DIR/messages/msg.txt` — overwrite every time, raw Slack text, no code fences. Then print the absolute file path.

Writing to a file is required because terminal indentation corrupts inline output.

## Process

1. Read user's draft or intent
2. Rewrite following rules and priority order above
3. Write to file — fully auto-pilot, no clarifying questions
