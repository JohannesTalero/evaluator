"""Tests for scripts/traspaso.sh"""
import os
import subprocess

import pytest

from conftest import GIT_ENV, _git

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
TRASPASO_SH = os.path.join(SCRIPTS_DIR, "traspaso.sh")
CHECK_SH = os.path.join(SCRIPTS_DIR, "check.sh")


def _setup_makefile(repo):
    """Create a minimal Makefile so make check-rapido works."""
    makefile = repo / "Makefile"
    makefile.write_text(
        ".PHONY: check-rapido\n"
        "check-rapido:\n"
        "\t@echo 'Ninguna area activa todavia. Nada que verificar.'\n"
    )
    check_sh = repo / "scripts" / "check.sh"
    check_sh.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECK_SH) as f:
        check_sh.write_text(f.read())
    check_sh.chmod(0o755)


def test_traspaso_genera_archivo(repo_tmp):
    _setup_makefile(repo_tmp)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add makefile")
    _git(repo_tmp, "checkout", "-b", "d1.2-carga-archivos")
    (repo_tmp / "api.py").write_text("print('hello')\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add api")

    result = subprocess.run(
        ["bash", TRASPASO_SH],
        cwd=repo_tmp, env=GIT_ENV,
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    archivo = repo_tmp / "progreso" / "d1.2.md"
    assert archivo.exists()
    contenido = archivo.read_text()
    assert "d1.2-carga-archivos" in contenido
    assert "Que falta" in contenido
    assert "Siguiente paso concreto" in contenido
    assert "api.py" in contenido


def test_traspaso_falla_en_main(repo_tmp):
    _setup_makefile(repo_tmp)
    result = subprocess.run(
        ["bash", TRASPASO_SH],
        cwd=repo_tmp, env=GIT_ENV,
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "main" in result.stderr


def test_traspaso_check_rapido_estado(repo_tmp):
    _setup_makefile(repo_tmp)
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add makefile")
    _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
    (repo_tmp / "code.py").write_text("x\n")
    _git(repo_tmp, "add", ".")
    _git(repo_tmp, "commit", "-m", "add code")

    subprocess.run(
        ["bash", TRASPASO_SH],
        cwd=repo_tmp, env=GIT_ENV,
        capture_output=True, text=True, check=True,
    )
    contenido = (repo_tmp / "progreso" / "b3.1.md").read_text()
    assert "PASA" in contenido
