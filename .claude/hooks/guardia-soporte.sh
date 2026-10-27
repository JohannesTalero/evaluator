#!/usr/bin/env bash
# Hook PreToolUse (Edit|Write): blocks editing support files
# outside a soporte-* branch.
set -uo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

RAMA=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

case "$RAMA" in
  soporte-*) exit 0 ;;
esac

ES_SOPORTE=false
case "$FILE_PATH" in
  *AGENTS.md|*CLAUDE.md) ES_SOPORTE=true ;;
  *.claude/*|*.codex/*|*.github/*) ES_SOPORTE=true ;;
  *scripts/*|*Makefile) ES_SOPORTE=true ;;
esac

if [ "$ES_SOPORTE" = true ]; then
  echo "Guardia de soporte: $FILE_PATH es un archivo de soporte." >&2
  echo "Solo se puede editar en una rama soporte-* (AGENTS.md, zonas de choque)." >&2
  exit 2
fi

exit 0
