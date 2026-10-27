#!/usr/bin/env python3
"""Checks that a PR doesn't exceed 300 changed lines.
Excludes lockfiles and auto-generated migrations.
Passes with the pr-grande-justificado label.
"""
import json
import os
import subprocess
import sys

LIMITE = 300
LOCKFILES = {
    "package-lock.json", "uv.lock", "pnpm-lock.yaml",
    "yarn.lock", "Pipfile.lock", "poetry.lock",
}


def es_excluido(ruta):
    nombre = os.path.basename(ruta)
    if nombre in LOCKFILES:
        return True
    if "/migrations/" in ruta and ruta.endswith(".py"):
        return True
    return False


def contar_lineas(base):
    result = subprocess.run(
        ["git", "diff", "--numstat", f"{base}...HEAD"],
        capture_output=True, text=True, check=True,
    )
    total = 0
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted, filepath = parts[0], parts[1], parts[2]
        if es_excluido(filepath):
            continue
        if added == "-" or deleted == "-":
            continue
        total += int(added) + int(deleted)
    return total


def obtener_etiquetas_ci():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return []
    with open(event_path) as f:
        event = json.load(f)
    pr = event.get("pull_request", {})
    return [label["name"] for label in pr.get("labels", [])]


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main")
    parser.add_argument("--label", action="append", default=[])
    args = parser.parse_args(argv)

    etiquetas = args.label if args.label else obtener_etiquetas_ci()

    if "pr-grande-justificado" in etiquetas:
        print(f"Etiqueta pr-grande-justificado presente, se omite el limite de {LIMITE} lineas.")
        return 0

    total = contar_lineas(args.base)
    print(f"Lineas cambiadas: {total} (limite: {LIMITE})")

    if total > LIMITE:
        print(f"FALLA: {total} lineas exceden el limite de {LIMITE}.")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
