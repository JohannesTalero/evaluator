"""Tests for scripts/relevo.sh with fake agents."""
import os
import subprocess
import stat
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.conftest import GIT_ENV, _git


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEVO_SH = os.path.join(ROOT, "scripts", "relevo.sh")


def _setup_repo(tmp_path, branch="d1.1-test"):
    """Create a temp repo on a task branch with the relay script available."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")

    # Minimal structure
    (repo / "progreso").mkdir()
    (repo / "tareas").mkdir()
    (repo / "scripts").mkdir()

    # Copy relevo-patrones.txt
    patrones_src = os.path.join(ROOT, "scripts", "relevo-patrones.txt")
    (repo / "scripts" / "relevo-patrones.txt").write_text(
        open(patrones_src).read()
    )

    # Minimal Makefile with check-rapido and traspaso
    (repo / "Makefile").write_text(
        ".PHONY: check-rapido traspaso\n"
        "check-rapido:\n"
        "\t@echo 'Nada que verificar'\n"
        "traspaso:\n"
        "\t@echo '# Traspaso' > progreso/d1.1.md\n"
    )

    (repo / "README.md").write_text("# Test\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")
    _git(repo, "checkout", "-b", branch)
    return repo


def _fake_agent(tmp_path, name, script_content):
    """Create a fake agent script that simulates behavior."""
    script = tmp_path / f"fake-{name}.sh"
    script.write_text(f"#!/usr/bin/env bash\n{script_content}\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return str(script)


def _run_relevo(repo, env_extra=None):
    """Run relevo.sh in the repo with given env overrides."""
    env = {**GIT_ENV, "ISSUE": "1", "RELEVO_ID": "d1.1"}
    if env_extra:
        env.update(env_extra)
    # Ensure PATH includes the scripts dir so make works
    env["PATH"] = os.environ.get("PATH", "/usr/bin:/bin")
    result = subprocess.run(
        ["bash", RELEVO_SH],
        cwd=repo, env=env,
        capture_output=True, text=True, timeout=30,
    )
    return result


class TestRelevoEnMain:
    def test_se_niega_en_main(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-b", "main")
        (repo / "README.md").write_text("# Test\n")
        _git(repo, "add", ".")
        _git(repo, "commit", "-m", "init")

        result = _run_relevo(repo)
        assert result.returncode != 0
        assert "main" in result.stderr.lower()


class TestCandado:
    def test_segundo_relevo_bloqueado(self, tmp_path):
        repo = _setup_repo(tmp_path)
        lockfile = repo / "progreso" / ".relevo-d1.1.lock"
        lockfile.write_text("99999")

        result = _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": "echo ok",
        })
        assert result.returncode != 0
        assert "ya existe" in result.stderr.lower() or "activo" in result.stderr.lower()


class TestCuotaYRelevo:
    def test_claude_sin_cuota_codex_termina(self, tmp_path):
        repo = _setup_repo(tmp_path)

        # Fake Claude: fails with quota message
        fake_claude = _fake_agent(tmp_path, "claude",
            "echo 'Error: rate limit exceeded'"
        )

        # Fake Codex: marks as done
        fake_codex = _fake_agent(tmp_path, "codex",
            f"echo 'estado: listo-para-pr' > {repo}/progreso/d1.1.md"
        )

        result = _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": f"bash {fake_claude}",
            "RELEVO_CODEX_CMD": f"bash {fake_codex}",
            "MAX_RELEVOS": "3",
        })
        assert result.returncode == 0
        assert "exito" in result.stdout.lower() or "ok" in result.stdout.lower()

        # Verify log exists
        logfile = repo / "progreso" / "relevo-d1.1.log"
        assert logfile.exists()
        log_content = logfile.read_text()
        assert "sin-cuota" in log_content
        assert "listo" in log_content

    def test_ambos_sin_cuota(self, tmp_path):
        repo = _setup_repo(tmp_path)

        fake_claude = _fake_agent(tmp_path, "claude",
            "echo 'quota exceeded'"
        )
        fake_codex = _fake_agent(tmp_path, "codex",
            "echo 'rate_limit reached'"
        )

        result = _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": f"bash {fake_claude}",
            "RELEVO_CODEX_CMD": f"bash {fake_codex}",
            "MAX_RELEVOS": "2",
        })
        assert result.returncode != 0

        logfile = repo / "progreso" / "relevo-d1.1.log"
        assert logfile.exists()


class TestErrorDesconocido:
    def test_error_no_pasa_turno(self, tmp_path):
        repo = _setup_repo(tmp_path)

        fake_claude = _fake_agent(tmp_path, "claude",
            "echo 'Segfault at 0x0'; exit 1"
        )

        result = _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": f"bash {fake_claude}",
        })
        assert result.returncode != 0
        assert "error" in result.stdout.lower() or "desconocido" in result.stdout.lower()

        logfile = repo / "progreso" / "relevo-d1.1.log"
        assert logfile.exists()
        assert "error" in logfile.read_text()


class TestListoPeroCheckFalla:
    def test_listo_pero_check_falla(self, tmp_path):
        repo = _setup_repo(tmp_path)

        # Override Makefile so check-rapido fails
        (repo / "Makefile").write_text(
            ".PHONY: check-rapido traspaso\n"
            "check-rapido:\n"
            "\t@echo 'FALLA'; exit 1\n"
            "traspaso:\n"
            "\t@echo '# Traspaso' > progreso/d1.1.md\n"
        )
        _git(repo, "add", "Makefile")
        _git(repo, "commit", "-m", "break check")

        fake_claude = _fake_agent(tmp_path, "claude",
            f"echo 'estado: listo-para-pr' > {repo}/progreso/d1.1.md"
        )

        result = _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": f"bash {fake_claude}",
        })
        assert result.returncode != 0
        assert "check" in result.stdout.lower() or "falla" in result.stdout.lower()


class TestCandadoSeLimpia:
    def test_candado_se_libera_al_terminar(self, tmp_path):
        repo = _setup_repo(tmp_path)

        fake_claude = _fake_agent(tmp_path, "claude",
            f"echo 'estado: listo-para-pr' > {repo}/progreso/d1.1.md"
        )

        _run_relevo(repo, {
            "RELEVO_CLAUDE_CMD": f"bash {fake_claude}",
        })

        lockfile = repo / "progreso" / ".relevo-d1.1.lock"
        assert not lockfile.exists()
