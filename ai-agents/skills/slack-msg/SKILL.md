---
name: slack-msg
kind: leaf
description: "Outgoing Slack/IM/DM message drafting for a coworker: rewrite or draft the short message the user is about to send, with clear meaning, polite tone, professional register, and Slack-native formatting. Use when: slack message, IM, DM, message a coworker, draft a message to send, make this message more polite/concise, reword before I send it, reply to a thread. NOT for: self-review or peer-feedback docs."
---

# Slack Message Writer

Rewrite or draft an outgoing workplace chat message that is correct, polite, professional, and concise.

## Priority order

1. **Correct and clear meaning** - fix weak collocations, ambiguity, articles, grammar, and technical phrasing while preserving intent.
2. **Polite tone** - warm and direct, never abrupt or passive-aggressive.
3. **Professional register** - match peer, leadership, or cross-team context.
4. **Concise structure** - lead with the point, then context, then next step.
5. **Slack-native formatting** - format for Slack, not Markdown previewers.

## Rewrite rules

- Resolve ambiguous phrasing by choosing the most likely reading from context; add one short assumption note when needed.
- Use short sentences and flat bullets for 2+ items.
- Keep all lines at column 0 so Slack preserves the layout.
- Use Slack formatting: `*bold*`, `_italic_`, `~strike~`, backticks, `> quote`, `<url|text>`, `- ` or `•` bullets.
- Render tables as aligned code blocks with emoji status icons.
- Ask for a clear next step when action is needed: `Could you review by Friday?` beats `Let me know`.

## Output

`SKILL_DIR` is the directory containing this file.

1. Create `$SKILL_DIR/messages/` if needed.
2. Overwrite `$SKILL_DIR/messages/msg.txt` with the raw Slack text, no code fences.
3. Print the absolute file path and any assumption note. Keep terminal output short because the file is the source of truth.

Writing to a file is required because terminal rendering can corrupt Slack indentation and inline formatting.
