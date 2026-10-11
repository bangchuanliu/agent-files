#!/bin/bash
# Deterministic pattern checks for slack-msg skill output.
#
# Usage:
#   pbpaste | bash check.sh          # check clipboard content
#   bash check.sh output.txt         # check a file
#
# 8 core checks — all must pass:
#
# Slack-native format (checks 1-5):
#   1. No markdown table syntax (| --- |)
#   2. No markdown bold (**text**)
#   3. No markdown headings (# text)
#   4. No markdown links [text](url)
#   5. Tables use code blocks (```) with emoji status + column alignment
#
# Tone — professional, concise, polite (checks 6-8):
#   6. No filler phrases ("Just wanted to", "Hope you're doing well", etc.)
#   7. At least one polite word (thanks, please, appreciate)
#   8. Output is concise (< 60% of input word count, if input provided)

set -uo pipefail

FILE="${1:-/dev/stdin}"
INPUT_FILE="${2:-}"  # optional: pass original input as 2nd arg for conciseness check
CONTENT=$(cat "$FILE")
PASS=0
FAIL=0

check_absent() {
  local label="$1" pattern="$2"
  if echo "$CONTENT" | grep -qE "$pattern"; then
    echo "FAIL: $label"
    ((FAIL++))
  else
    echo "PASS: $label"
    ((PASS++))
  fi
}

check_present() {
  local label="$1" pattern="$2"
  if echo "$CONTENT" | grep -qE "$pattern"; then
    echo "PASS: $label"
    ((PASS++))
  else
    echo "FAIL: $label"
    ((FAIL++))
  fi
}

echo "=== slack-msg output checks ==="
echo ""

# 1. No markdown table separators
check_absent "No markdown tables (|---|)" '\| *-{2,} *\|'

# 2. No markdown double-asterisk bold
check_absent "No markdown bold (**text**)" '\*\*[^*]+\*\*'

# 3. No markdown headings
check_absent "No markdown headings (# text)" '^#{1,6} '

# 4. No markdown links
check_absent "No markdown links [text](url)" '\[.+\]\(http'

# 5. If table-like content exists: code block + emoji status + column alignment
HAS_TABLE=$(echo "$CONTENT" | grep -cE '(✅|🔄|🚫|⚠️)' || true)
if [ "$HAS_TABLE" -gt 0 ]; then
  check_present "Tables wrapped in code block (\`\`\`)" '```'
  check_present "Table has emoji status icons (✅/🔄/🚫)" '(✅|🔄|🚫)'
  check_present "Table has column separator line (───)" '─{3,}'
else
  echo "SKIP: No tabular data detected (checks 5a-5c skipped)"
fi

echo ""
echo "=== Tone: professional, concise, polite ==="
echo ""

# 6. No filler phrases
check_absent "No filler: 'Just wanted to'" '[Jj]ust wanted to'
check_absent "No filler: 'Hope you.re doing well'" '[Hh]ope you.re doing well'
check_absent "No filler: 'I was wondering if'" '[Ii] was wondering if'
check_absent "No filler: 'no rush'" '[Nn]o rush'
check_absent "No filler: 'when you get a chance'" 'when you get a chance'

# 7. At least one polite word
check_present "Has polite language (thanks/please/appreciate)" '([Tt]hanks|[Pp]lease|[Aa]ppreciate)'

# 8. Conciseness check (requires input file as 2nd arg)
if [ -n "$INPUT_FILE" ] && [ -f "$INPUT_FILE" ]; then
  INPUT_WORDS=$(wc -w < "$INPUT_FILE" | tr -d ' ')
  OUTPUT_WORDS=$(echo "$CONTENT" | wc -w | tr -d ' ')
  RATIO=$(( OUTPUT_WORDS * 100 / INPUT_WORDS ))
  if [ "$RATIO" -le 60 ]; then
    echo "PASS: Concise — output is ${RATIO}% of input word count (${OUTPUT_WORDS}/${INPUT_WORDS} words)"
    ((PASS++))
  else
    echo "FAIL: Not concise — output is ${RATIO}% of input (${OUTPUT_WORDS}/${INPUT_WORDS} words, need ≤60%)"
    ((FAIL++))
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
