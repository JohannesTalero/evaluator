#!/usr/bin/env bash
# Detects active areas and runs their tools (decision 0003).
# Usage: check.sh [--rapido] [--area api|front|infra]
set -uo pipefail

RAPIDO=false
AREA=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rapido) RAPIDO=true; shift ;;
    --area)   AREA="$2"; shift 2 ;;
    *)        echo "Argumento desconocido: $1" >&2; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORES=0

check_api() {
  echo "=== api/ ==="
  cd "$ROOT/api"
  uv run ruff check . || ERRORES=1
  uv run pytest || ERRORES=1
  if [ "$RAPIDO" = false ]; then
    uv run bandit -r . -c pyproject.toml 2>/dev/null || ERRORES=1
    uv run pip-audit 2>/dev/null || ERRORES=1
  fi
  cd "$ROOT"
}

check_front() {
  echo "=== front/ ==="
  cd "$ROOT/front"
  npm run lint || ERRORES=1
  npm run test || ERRORES=1
  if [ "$RAPIDO" = false ]; then
    npm audit || ERRORES=1
  fi
  cd "$ROOT"
}

check_infra() {
  echo "=== infra/ ==="
  cd "$ROOT/infra"
  terraform fmt -check -recursive || ERRORES=1
  terraform validate || ERRORES=1
  if [ "$RAPIDO" = false ]; then
    checkov -d . || ERRORES=1
  fi
  cd "$ROOT"
}

API_ACTIVE=false
FRONT_ACTIVE=false
INFRA_ACTIVE=false

[ -f "$ROOT/api/pyproject.toml" ] && API_ACTIVE=true
[ -f "$ROOT/front/package.json" ] && FRONT_ACTIVE=true
[ -d "$ROOT/infra" ] && [ -n "$(find "$ROOT/infra" -name '*.tf' -print -quit 2>/dev/null)" ] && INFRA_ACTIVE=true

if [ -n "$AREA" ]; then
  case "$AREA" in
    api)
      if [ "$API_ACTIVE" = true ]; then check_api
      else echo "api/ no activa (falta api/pyproject.toml)" >&2; exit 1; fi ;;
    front)
      if [ "$FRONT_ACTIVE" = true ]; then check_front
      else echo "front/ no activa (falta front/package.json)" >&2; exit 1; fi ;;
    infra)
      if [ "$INFRA_ACTIVE" = true ]; then check_infra
      else echo "infra/ no activa (falta infra/**/*.tf)" >&2; exit 1; fi ;;
    *) echo "Area desconocida: $AREA" >&2; exit 1 ;;
  esac
else
  ALGUNA=false
  if [ "$API_ACTIVE" = true ];   then ALGUNA=true; check_api;   fi
  if [ "$FRONT_ACTIVE" = true ]; then ALGUNA=true; check_front; fi
  if [ "$INFRA_ACTIVE" = true ]; then ALGUNA=true; check_infra; fi

  if [ "$ALGUNA" = false ]; then
    echo "Ninguna area activa todavia. Nada que verificar."
    exit 0
  fi
fi

if [ "$ERRORES" -ne 0 ]; then
  echo "Hubo errores." >&2
  exit 1
fi
echo "Todo en verde."
