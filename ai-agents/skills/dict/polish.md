# Prompt Polish Rubric

Rewrite a user's draft prompt so it's concise, clear, and friendly for an AI coding agent. The polished prompt must preserve the user's original intent — never silently expand scope or change goals.

## What "agent-friendly" means

A polished prompt should:

1. **Lead with the goal in one line.** What outcome does the user want? State it before any context.
2. **Name concrete artifacts.** File paths, line numbers, function names, exact commands, exact error messages. The agent shouldn't have to guess what "the file" or "the bug" refers to.
3. **State constraints up front.** Must / must-not / out-of-scope before nice-to-haves. Constraints prevent wasted exploration.
4. **Specify expected output format.** "Diff only", "bullet list under 100 words", "single command", "JSON". Without this, the agent guesses.
5. **Drop hedging and politeness fillers.** Cut: *could you maybe, I was wondering if, if possible, I think, kind of, sort of, please*. Keep tone direct, not curt.
6. **Cap response length** when a short answer is fine. ("Under 50 words", "one paragraph", "one command".)
7. **Don't outsource synthesis.** Avoid "based on your findings, implement…" — that pushes thinking onto the agent. Instead, the user should pre-decide and write the decision into the prompt.

## What NOT to do

- **Don't add scope** the user didn't ask for (no extra "while you're at it…").
- **Don't invent file paths or line numbers.** If the original prompt is vague, leave a placeholder like `<file path>` and flag it in the change notes.
- **Don't make the prompt longer than the original** unless it was missing critical structure. Polishing is mostly subtraction.
- **Don't change the language** (English ↔ another language) unless the user asks.
- **Don't strip context the agent actually needs** to make judgment calls. Polishing is not summarizing.

## Output format

```
### Polished
<the rewritten prompt — copy-paste ready>

### Changes
- <one-line note about what changed and why>
- <another change>

### Flags (if any)
- <missing detail that would make this even better, e.g., "no file path given — agent will need to search">
```

If the original prompt is already clean, say so explicitly: `Already concise — no rewrite needed.` Don't polish for the sake of it.

## Example

**Original (draft):**
> hey could you maybe take a look at the auth thing in our user service and see if there's anything weird going on with the token expiry, I think there might be a bug or something but I'm not 100% sure, also if you could write some tests that would be great

**Polished:**
> Audit `services/user-service/auth.py` for token-expiry bugs. If you find one, write a regression test in `tests/test_auth.py`. Report findings as: bug location, root cause, fix diff. Under 200 words.

**Changes:**
- Removed hedging (*maybe, I think, or something, not 100% sure*).
- Replaced "the auth thing in our user service" with a concrete file path placeholder — flag below.
- Made the test ask conditional on finding a bug (avoids speculative test writing).
- Added an output format and length cap.

**Flags:**
- File path was assumed. Confirm before submitting if the actual path differs.
