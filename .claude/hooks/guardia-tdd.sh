#!/usr/bin/env bash
# Hook PreToolUse (Edit|Write): blocks editing production code in api/ or front/
# if the branch diff doesn't touch any test file yet.
# Reads JSON from stdin with tool_input.file_path.
set -uo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

RAMA=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
if [ "$RAMA" = "main" ] || [ "$RAMA" = "HEAD" ]; then
  exit 0
fi

case "$FILE_PATH" in
  */api/*|api/*) AREA="api" ;;
  */front/*|front/*) AREA="front" ;;
  *) exit 0 ;;
esac

case "$FILE_PATH" in
  *test*|*spec*|*__tests__*|*_test.py|*_test.ts|*_test.tsx) exit 0 ;;
esac

DIFF_STAGED=$(git diff --cached --name-only 2>/dev/null || true)
DIFF_BRANCH=$(git diff --name-only main...HEAD 2>/dev/null || true)
DIFF_UNSTAGED=$(git diff --name-only 2>/dev/null || true)
ALL_CHANGES=$(printf "%s\n%s\n%s" "$DIFF_STAGED" "$DIFF_BRANCH" "$DIFF_UNSTAGED")

HAS_TEST=$(echo "$ALL_CHANGES" | grep -iE "(test|spec|__tests__)" || true)

if [ -z "$HAS_TEST" ]; then
  echo "Guardia TDD: estas editando codigo de produccion en $AREA/ pero el diff de la rama no toca ningun test." >&2
  echo "Escribe primero un test que falle (TDD). Si este archivo no necesita test, dilo y detente." >&2
  exit 2
fi

exit 0
