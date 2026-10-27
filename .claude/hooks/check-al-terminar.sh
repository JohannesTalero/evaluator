#!/usr/bin/env bash
# Hook Stop: runs make check-rapido and blocks if it fails.
# Uses stop_hook_active from stdin to prevent re-entrance.
set -uo pipefail

INPUT=$(cat)
STOP_ACTIVE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('stop_hook_active', False))" 2>/dev/null)

if [ "$STOP_ACTIVE" = "True" ] || [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

RAMA=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
if [ "$RAMA" = "main" ] || [ "$RAMA" = "HEAD" ]; then
  exit 0
fi

OUTPUT=$(make check-rapido 2>&1) || {
  echo "check-al-terminar: make check-rapido fallo. Arregla los errores antes de terminar." >&2
  echo "$OUTPUT" | tail -20 >&2
  exit 2
}

exit 0
