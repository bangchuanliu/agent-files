---
name: slack-msg
kind: leaf
description: "Use when: drafting or rewording a short Slack/IM/DM message the user is about to send to a coworker - draft a new message, make a draft more polite or concise (reword before I send it), or reply in a thread - written to a local HTML file to open, copy, and paste into Slack with formatting. NOT for: framing your own work for impact (self-assessment), feedback about a colleague (peer-feedback), or a readout (template-general-readout)."
---

# Slack Message Writer

## Objective

Draft or rewrite a short outgoing workplace chat message and write it as a private local HTML file. The user opens the file in a browser, selects all, copies, and pastes into Slack, which keeps the bold, italics, code, links, lists, and quotes. The message must say what the user means, correctly, in a polite and professional tone that fits the recipient (peer, leadership, or cross-team).

Success: the file holds only the message, formatted with Slack-pasteable HTML; the user's intent and every fact, number, date, and offer in their draft survive; and `evals/check.sh` passes on the file.

## Guardrails & Constraints

- MUST preserve the user's intent and every fact, number, date, name, channel, and offer from their draft; shorten wording, never content.
- WHEN goals conflict, MUST rank them: correct and clear meaning, then polite tone, then professional register, then concision, then Slack formatting.
- IF the draft is ambiguous, MUST pick the most likely reading from context and add one short assumption note to the terminal output, not the message.
- MUST write the message to `$SKILL_DIR/messages/msg.html` (`SKILL_DIR` is the directory containing this file; create `messages/` if needed), overwriting it, as a standalone HTML document (`<!DOCTYPE html>`, `<meta charset="utf-8">`, message inside `<body>`). A file is required because terminal rendering corrupts formatting, and HTML is required because copying rendered HTML from a browser carries the formatting into Slack, which plain text does not.
- MUST keep message text out of git, because it is private: `messages/` is gitignored, so never stage or commit it. IF `git check-ignore` does not report the file as ignored while it sits inside a git work tree, MUST write to `~/.cache/slack-msg/msg.html` instead and say so.
- MUST format only with tags Slack keeps on paste: `<b>`, `<i>`, `<s>`, `<code>`, `<pre>`, `<a href="...">`, `<ul>`/`<ol>`/`<li>`, `<blockquote>`, `<p>`, `<br>`. No CSS, `<h1>`-`<h6>`, `<table>`, images, or nested lists, because Slack drops or flattens them.
- MUST NOT put Markdown or Slack mrkdwn markers in the text (`**bold**`, `*bold*`, `_italic_`, `# heading`, `[text](url)`, `<url|text>`, triple-backtick fences, `| --- |` tables), because pasted rich text shows them literally. Escape `&`, `<`, and `>` in message text as `&amp;`, `&lt;`, `&gt;`.
- IF the message contains a table, MUST render it inside `<pre>` with aligned columns, a `───` rule under the header row, and emoji status icons (e.g. ✅ 🔄 🚫 ⚠️).

## Preferences

- SHOULD fix weak collocations, articles, grammar, and technical phrasing while keeping the user's voice.
- SHOULD use short sentences, and flat bullets for 2+ items.
- SHOULD cut filler (e.g. "just wanted to", "I was wondering if", "hope you're doing well", "when you get a chance", "no rush") and include a thanks or please.
- IF action is needed, SHOULD end with a concrete ask and timing: `Could you review by Friday?` beats `Let me know`.
- IF rewriting, SHOULD land at or under 60% of the original word count unless that would drop content.

## Output

- Open the file in the default browser (`open <file>` on macOS, `xdg-open <file>` on Linux) so the user can select all, copy, and paste into Slack.
- Print the absolute path of the message file and any assumption note. Keep terminal output short; the file is the source of truth.

## Verification

- `bash evals/check.sh <message-file> [original-draft-file]` passes; pass the original when rewriting so the concision check runs. IF a check fails for a deliberate reason (e.g. no polite word fits a terse FYI), state which and why.
- The file is ignored by git (`git check-ignore <message-file>`) or lives outside any repo.
- Every fact, number, date, and offer from the user's draft appears in the message.
