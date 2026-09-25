#!/usr/bin/env bash
# One entrypoint for every repo check: shell syntax (+ shellcheck when installed), Python
# compile, skill spec lint, every skill's own tests, and the sandboxed installer test.
# Run before committing: tests/run.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 2
failed=()
step() {
  local name="$1"; shift
  echo "=== $name"
  if "$@"; then echo "--- pass: $name"; else echo "--- FAIL: $name"; failed+=("$name"); fi
}

shell_files() {
  git ls-files -co --exclude-standard -z -- '*.sh' 'ai-agents/skills/*/scripts/*' \
    | xargs -0 grep -lE '^#!.*\b(ba)?sh\b' 2>/dev/null
}
syntax() { local f rc=0; while IFS= read -r f; do bash -n "$f" || rc=1; done < <(shell_files); return $rc; }
lint() {
  if ! command -v shellcheck >/dev/null; then echo "shellcheck not installed; skipped"; return 0; fi
  shell_files | xargs shellcheck -S warning
}
pycompile() {
  git ls-files -co --exclude-standard -z -- '*.py' \
    | xargs -0 python3 -c 'import sys; [compile(open(f, encoding="utf-8").read(), f, "exec") for f in sys.argv[1:]]'
}
spec() { python3 ai-agents/skills/skill-improver/scripts/spec_check.py --all ai-agents/skills; }
skill_tests() {
  local t rc=0
  while IFS= read -r t; do
    echo "--> $t"
    (cd "$(dirname "$t")" && python3 "$(basename "$t")") || rc=1
  done < <(git ls-files -co --exclude-standard -- 'ai-agents/skills/**/test_*.py')
  return $rc
}

step "shell syntax" syntax
step "shellcheck" lint
step "python compile" pycompile
step "skill spec" spec
step "skill tests" skill_tests
step "installer" bash tests/test_install.sh

echo ""
if [ ${#failed[@]} -eq 0 ]; then echo "ALL CHECKS PASSED"; else echo "FAILED: ${failed[*]}"; exit 1; fi
