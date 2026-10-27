"""Load a golden set from a local directory."""
from __future__ import annotations

import json
from pathlib import Path

from evals.schema import GoldenSet


def load_golden_set(directory: Path | str) -> GoldenSet:
    """Load and validate a golden set from a directory containing manifest.json."""
    directory = Path(directory)
    manifest_path = directory / "manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {directory}")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    gs = GoldenSet.from_dict(data)

    for page in gs.exam_pages:
        if not (directory / page).exists():
            raise FileNotFoundError(f"exam page not found: {page}")

    for student in gs.students:
        for page in student.pages:
            if not (directory / page).exists():
                raise FileNotFoundError(f"student page not found: {page}")

    return gs
