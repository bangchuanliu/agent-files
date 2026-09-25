---
name: dict
kind: leaf
description: "Practice the user's own English: personal vocabulary capture, sentence rewrites for language learning, learning progress, dictionary preview, prompt polish, and workplace dialogue drills. Use when: vocab, save word, look up word, extract verbs, tech verbs, review my sentences, fix my sentences in this thread, I used X today, graduate X, show progress, preview dict, start dict server, stop dict server, polish prompt, tighten prompt, small talk, debate, meeting scenario, demo scenario. NOT for: drafting an outgoing coworker Slack/IM/DM to send - use slack-msg; peer review or self-review writing; general grammar checking detached from the user's learning dictionary."
---

# Personal Dictionary & Communication Coach

Pick one mode from the user's request, then read its rubric before responding. The rubrics carry the exact operation specs, output format, and storage rules.

| Mode | Use for | Rubric |
|------|---------|--------|
| **Dictionary practice** | Save, look up, list, extract, or curate vocabulary; rewrite the user's own sentences for language practice; update progress; preview or stop the dictionary server. | [`vocab.md`](vocab.md) |
| **Prompt polish** | Rewrite a draft prompt for an AI agent while preserving the user's scope. | [`polish.md`](polish.md) |
| **Scenario coaching** | Generate workplace dialogue drills with word banks. | [`coach.md`](coach.md) |

Boundary: this skill practices the user's own English and prompt-writing. If the user is composing a real outgoing message to a coworker, route to `slack-msg`.
