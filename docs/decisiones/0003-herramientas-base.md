# 0003 — Herramientas base de cada área

- Fecha: 2026-10-27
- Estado: propuesta (se confirma en B1.1, B2.3 y A1.1)

## Contexto

`scripts/check.sh` y CI necesitan comandos concretos por área. El documento del proyecto ya nombra ruff, pytest, Alembic, eslint, vitest y Terraform.

## Decisión

| Área | Herramientas | Archivo que activa el área en CI |
| --- | --- | --- |
| `api/` | Python 3.12, uv, FastAPI, SQLAlchemy 2, Alembic, ruff, pytest, bandit, pip-audit | `api/pyproject.toml` |
| `front/` | Node 22, npm, Vite, React, TypeScript, eslint, vitest | `front/package.json` |
| `infra/` | Terraform, checkov | algún `infra/**/*.tf` |

`front/package.json` debe tener los scripts `lint` y `test` (vitest en modo no interactivo).

## Consecuencias

Cambiar una herramienta es un PR `soporte` que actualiza esta tabla, `scripts/check.sh` y CI juntos.
