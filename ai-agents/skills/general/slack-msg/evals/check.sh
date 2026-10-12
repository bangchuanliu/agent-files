#!/bin/bash
# Deterministic pattern checks for slack-msg skill output (an HTML file).
#
# Usage:
#   bash check.sh messages/msg.html                 # check a file
#   bash check.sh messages/msg.html draft.txt       # also run the conciseness check
#
# Core checks - all must pass (SKILL.md states the rules they enforce):
#
# HTML structure (checks 1-3):
#   1. Standalone HTML document (<!DOCTYPE html>, utf-8 charset, <body>)
#   2. Only Slack-pasteable tags (b, i, s, code, pre, a, ul, ol, li, blockquote, p, br)
#   3. No inline CSS or <style> blocks
#
# No Markdown or Slack mrkdwn markers in the text (checks 4-9):
#   4. No markdown table syntax (| --- |)
#   5. No markdown bold (**text**)
#   6. No markdown headings (# text)
#   7. No markdown links [text](url)
#   8. No Slack mrkdwn links &lt;url|text&gt;
#   9. No triple-backtick fences
#
#  10. Tables (2+ lines with status emoji) use <pre> with emoji status icons
#      and a ─── rule under the header row
#
# Tone - professional, concise, polite (checks 11-13), on tag-stripped text:
#  11. No filler phrases ("Just wanted to", "Hope you're doing well", etc.)
#  12. At least one polite word (thanks, please, appreciate)
#  13. Output is concise (<= 60% of input word count, if input provided)

set -uo pipefail

FILE="${1:-/dev/stdin}"
INPUT_FILE="${2:-}"
CONTENT=$(cat "$FILE")
BODY=$(echo "$CONTENT" | tr '\n' '\r' | sed -E 's/.*<body[^>]*>//I; s/<\/body>.*//I' | tr '\r' '\n')
TEXT=$(echo "$BODY" | sed -E 's/<[^>]*>/ /g; s/&nbsp;/ /g; s/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g')
PASS=0
FAIL=0

result() {
  if [ "$1" -eq 0 ]; then echo "PASS: $2"; ((PASS++)); else echo "FAIL: $2"; ((FAIL++)); fi
}

check_absent() {
  local label="$1" pattern="$2" haystack="$3"
  echo "$haystack" | grep -qE -- "$pattern"
  result $(( $? == 0 )) "$label"
}

check_present() {
  local label="$1" pattern="$2" haystack="$3"
  echo "$haystack" | grep -qE -- "$pattern"
  result $(( $? != 0 )) "$label"
}

echo "=== slack-msg output checks ==="
echo ""

# 1. Standalone HTML document
check_present "Has <!DOCTYPE html>" '^[[:space:]]*<!DOCTYPE html>' "$(echo "$CONTENT" | head -1)"
check_present "Declares utf-8 charset" '<meta charset="?utf-8"?' "$CONTENT"
check_present "Has <body>" '<body[ >]' "$CONTENT"

# 2. Only Slack-pasteable tags inside <body>
BAD_TAGS=$(echo "$BODY" | grep -oE '</?[a-zA-Z][a-zA-Z0-9]*' | sed -E 's#</?##' | tr 'A-Z' 'a-z' | sort -u \
  | grep -vxE 'b|strong|i|em|s|del|code|pre|a|ul|ol|li|blockquote|p|br' | tr '\n' ' ')
if [ -z "$BAD_TAGS" ]; then
  result 0 "Only Slack-pasteable tags in body"
else
  result 1 "Only Slack-pasteable tags in body (found: $BAD_TAGS)"
fi

# 3. No CSS
check_absent "No inline CSS or <style>" '(<style|style=)' "$CONTENT"

# 4-9. No Markdown or Slack mrkdwn markers in the visible text
check_absent "No markdown tables (|---|)" '\| *-{2,} *\|' "$TEXT"
check_absent "No markdown bold (**text**)" '\*\*[^*]+\*\*' "$TEXT"
check_absent "No markdown headings (# text)" '^[[:space:]]*#{1,6} ' "$TEXT"
check_absent "No markdown links [text](url)" '\[.+\]\(http' "$TEXT"
check_absent "No Slack mrkdwn links <url|text>" '<https?://[^>|]+\|' "$TEXT"
check_absent "No triple-backtick fences" '```' "$TEXT"

# 10. If table-like content exists: <pre> + emoji status + header rule.
HAS_TABLE=$(echo "$TEXT" | grep -cE '(✅|🔄|🚫|⚠️)' || true)
if [ "$HAS_TABLE" -ge 2 ]; then
  check_present "Tables wrapped in <pre>" '<pre[ >]' "$BODY"
  check_present "Table has emoji status icons (✅/🔄/🚫)" '(✅|🔄|🚫)' "$TEXT"
  check_present "Table has header rule (───)" '─{3,}' "$TEXT"
else
  echo "SKIP: No tabular data detected (table checks skipped)"
fi

echo ""
echo "=== Tone: professional, concise, polite ==="
echo ""

# 11. No filler phrases
check_absent "No filler: 'Just wanted to'" '[Jj]ust wanted to' "$TEXT"
check_absent "No filler: 'Hope you.re doing well'" '[Hh]ope you.re doing well' "$TEXT"
check_absent "No filler: 'I was wondering if'" '[Ii] was wondering if' "$TEXT"
check_absent "No filler: 'no rush'" '[Nn]o rush' "$TEXT"
check_absent "No filler: 'when you get a chance'" 'when you get a chance' "$TEXT"

# 12. At least one polite word
check_present "Has polite language (thanks/please/appreciate)" '([Tt]hanks|[Pp]lease|[Aa]ppreciate)' "$TEXT"

# 13. Conciseness check (requires input file as 2nd arg)
if [ -n "$INPUT_FILE" ] && [ -f "$INPUT_FILE" ]; then
  INPUT_WORDS=$(wc -w < "$INPUT_FILE" | tr -d ' ')
  OUTPUT_WORDS=$(echo "$TEXT" | wc -w | tr -d ' ')
  RATIO=$(( OUTPUT_WORDS * 100 / INPUT_WORDS ))
  if [ "$RATIO" -le 60 ]; then
    result 0 "Concise - output is ${RATIO}% of input word count (${OUTPUT_WORDS}/${INPUT_WORDS} words)"
  else
    result 1 "Not concise - output is ${RATIO}% of input (${OUTPUT_WORDS}/${INPUT_WORDS} words, need <=60%)"
  fi
else
  echo "SKIP: No input file provided (pass as 2nd arg for conciseness check)"
fi

echo ""
echo "--- $PASS passed, $FAIL failed ---"
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "SOME CHECKS FAILED"
fi
exit "$FAIL"
