"""Tests for scripts/ci/alcance.py"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "ci"))

import alcance
from conftest import GIT_ENV, _git


def test_parsear_alcance_basico():
    body = "## PR\nalcance: api/**\n## Que hace"
    assert alcance.parsear_alcance(body) == ["api/**"]


def test_parsear_alcance_multiples_globs():
    body = "alcance: api/**, front/src/**"
    assert alcance.parsear_alcance(body) == ["api/**", "front/src/**"]


def test_parsear_alcance_ausente():
    body = "## PR\nEste PR no tiene la linea de alcance."
    assert alcance.parsear_alcance(body) is None


def test_parsear_alcance_case_insensitive():
    body = "Alcance: api/**"
    assert alcance.parsear_alcance(body) == ["api/**"]


def test_parsear_alcance_con_espacios():
    body = "  alcance:   api/**  ,  front/**  "
    assert alcance.parsear_alcance(body) == ["api/**", "front/**"]


def test_archivo_en_alcance_basico():
    assert alcance.archivo_en_alcance("api/main.py", ["api/**"]) is True
    assert alcance.archivo_en_alcance("front/App.tsx", ["api/**"]) is False


def test_archivo_en_alcance_glob_doble_asterisco():
    assert alcance.archivo_en_alcance("api/routers/auth.py", ["api/**"]) is True
    assert alcance.archivo_en_alcance("api/tests/test_auth.py", ["api/**"]) is True


def test_progreso_siempre_permitido():
    assert alcance.archivo_en_alcance("progreso/d1.2.md", ["api/**"]) is True
    assert alcance.archivo_en_alcance("progreso/sub/file.md", ["api/**"]) is True


def test_archivo_fuera_del_alcance():
    assert alcance.archivo_en_alcance("infra/main.tf", ["api/**"]) is False


def test_es_archivo_soporte():
    assert alcance.es_archivo_soporte("AGENTS.md") is True
    assert alcance.es_archivo_soporte(".claude/settings.json") is True
    assert alcance.es_archivo_soporte("scripts/check.sh") is True
    assert alcance.es_archivo_soporte(".github/workflows/ci.yml") is True
    assert alcance.es_archivo_soporte("api/main.py") is False


def test_soporte_con_etiqueta(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "scripts").mkdir(exist_ok=True)
    (repo_tmp / "scripts" / "nuevo.sh").write_text("#!/bin/bash\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add support file")
    os.chdir(repo_tmp)
    result = alcance.main([
        "--base", "main",
        "--body", "alcance: api/**",
        "--label", "soporte",
    ])
    assert result == 0


def test_soporte_sin_etiqueta_falla(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "scripts").mkdir(exist_ok=True)
    (repo_tmp / "scripts" / "nuevo.sh").write_text("#!/bin/bash\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add support file")
    os.chdir(repo_tmp)
    result = alcance.main([
        "--base", "main",
        "--body", "alcance: api/**",
    ])
    assert result == 1


def test_alcance_ausente_falla(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "algo.py").write_text("x\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add file")
    os.chdir(repo_tmp)
    result = alcance.main([
        "--base", "main",
        "--body", "Este PR no tiene alcance",
    ])
    assert result == 1
