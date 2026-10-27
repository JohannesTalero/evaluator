#!/usr/bin/env python3
"""Checks that all changed files fall within the PR's declared scope.
Reads the 'alcance:' line from the PR body.
progreso/** is always allowed.
Support files require the 'soporte' label.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys

PATRONES_SOPORTE = [
    "AGENTS.md", "CLAUDE.md", "Makefile",
    ".claude/*", ".claude/**", ".codex/*", ".codex/**",
    ".github/*", ".github/**", "scripts/*", "scripts/**",
    "docs/*", "docs/**",
]


def parsear_alcance(body):
    if not body:
        return None
    for line in body.split("\n"):
        m = re.match(r"^\s*alcance:\s*(.+)", line, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            globs = [g.strip() for g in re.split(r"[,\s]+", raw) if g.strip()]
            return globs if globs else None
    return None


def es_archivo_soporte(filepath):
    for pattern in PATRONES_SOPORTE:
        if fnmatch.fnmatch(filepath, pattern):
            return True
    return False


def archivo_en_alcance(filepath, globs):
    if filepath.startswith("progreso/") or fnmatch.fnmatch(filepath, "progreso/**"):
        return True
    for glob in globs:
        if fnmatch.fnmatch(filepath, glob):
            return True
    return False


def obtener_archivos_cambiados(base):
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def obtener_pr_ci():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return None, []
    with open(event_path) as f:
        event = json.load(f)
    pr = event.get("pull_request", {})
    body = pr.get("body", "")
    labels = [label["name"] for label in pr.get("labels", [])]
    return body, labels


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main")
    parser.add_argument("--body-file", help="File with PR body")
    parser.add_argument("--body", help="PR body as string")
    parser.add_argument("--label", action="append", default=[])
    args = parser.parse_args(argv)

    if args.body:
        body = args.body
        etiquetas = args.label
    elif args.body_file:
        with open(args.body_file) as f:
            body = f.read()
        etiquetas = args.label
    else:
        body, etiquetas = obtener_pr_ci()
        if body is None:
            print("FALLA: no se encontro el cuerpo del PR.")
            return 1
        etiquetas = etiquetas or args.label

    globs = parsear_alcance(body)
    if globs is None:
        print("FALLA: no se encontro la linea 'alcance:' en el cuerpo del PR.")
        return 1

    archivos = obtener_archivos_cambiados(args.base)
    fuera = []
    for filepath in archivos:
        if archivo_en_alcance(filepath, globs):
            continue
        if es_archivo_soporte(filepath) and "soporte" in etiquetas:
            continue
        fuera.append(filepath)

    if fuera:
        print(f"FALLA: {len(fuera)} archivo(s) fuera del alcance:")
        for f in fuera:
            print(f"  - {f}")
        return 1

    print(f"OK: {len(archivos)} archivo(s) dentro del alcance ({', '.join(globs)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
