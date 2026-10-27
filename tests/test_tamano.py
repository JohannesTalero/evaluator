"""Tests for scripts/ci/tamano.py"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "ci"))

import tamano
from conftest import GIT_ENV, _git


def test_es_excluido_lockfile():
    assert tamano.es_excluido("package-lock.json") is True
    assert tamano.es_excluido("front/package-lock.json") is True
    assert tamano.es_excluido("uv.lock") is True


def test_es_excluido_migracion():
    assert tamano.es_excluido("api/migrations/versions/001_init.py") is True


def test_no_excluido_archivo_normal():
    assert tamano.es_excluido("api/main.py") is False
    assert tamano.es_excluido("front/src/App.tsx") is False


def test_diff_vacio(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    os.chdir(repo_tmp)
    assert tamano.contar_lineas("main") == 0


def test_cuenta_lineas(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "nuevo.py").write_text("line\n" * 50)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add 50 lines")
    os.chdir(repo_tmp)
    assert tamano.contar_lineas("main") == 50


def test_400_lineas_falla(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "grande.py").write_text("x\n" * 400)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add 400 lines")
    os.chdir(repo_tmp)
    assert tamano.main(["--base", "main"]) == 1


def test_con_etiqueta_pasa(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "grande.py").write_text("x\n" * 400)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add 400 lines")
    os.chdir(repo_tmp)
    assert tamano.main(["--base", "main", "--label", "pr-grande-justificado"]) == 0


def test_lockfile_no_cuenta(repo_tmp):
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    (repo_tmp / "package-lock.json").write_text("{}\n" * 500)
    (repo_tmp / "code.py").write_text("x\n" * 10)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add lockfile and code")
    os.chdir(repo_tmp)
    assert tamano.contar_lineas("main") == 10


def test_archivo_renombrado(repo_tmp):
    (repo_tmp / "old.py").write_text("content\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add old.py")
    _git(repo_tmp, "checkout", "-b", "a1.1-test")
    _git(repo_tmp, "mv", "old.py", "new.py")
    _git(repo_tmp, "commit", "-m", "rename")
    os.chdir(repo_tmp)
    assert tamano.contar_lineas("main") == 0
