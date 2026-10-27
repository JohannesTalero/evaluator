.PHONY: check check-rapido check-api check-front check-infra traspaso issues issues-crear relevo

check:
	@bash scripts/check.sh

check-rapido:
	@bash scripts/check.sh --rapido

check-api:
	@bash scripts/check.sh --area api

check-front:
	@bash scripts/check.sh --area front

check-infra:
	@bash scripts/check.sh --area infra

traspaso:
	@bash scripts/traspaso.sh

issues:
	@uv run --with pyyaml python scripts/issues.py

issues-crear:
	@uv run --with pyyaml python scripts/issues.py --crear

relevo:
	@bash scripts/relevo.sh
