"""Fixtures shared by every test in this folder and below it.

pytest finds this file automatically. Any test can use one of these fixtures
just by naming it as a parameter.
"""

import json
import shutil
from pathlib import Path

import pytest

FIXTURE_EXPORTS = Path(__file__).parent / "fixtures" / "exports"


@pytest.fixture
def sla_hours() -> dict[str, int]:
    return {"P1": 4, "P2": 24, "P3": 72, "P4": 168}


@pytest.fixture
def sample_exports(tmp_path: Path) -> Path:
    """A private copy of the sample export folder, so no test can damage the original."""
    target = tmp_path / "data" / "exports"
    shutil.copytree(FIXTURE_EXPORTS, target)
    return target


@pytest.fixture
def config_file(tmp_path: Path, sample_exports: Path, sla_hours: dict[str, int]) -> Path:
    """A config.json next to the copied sample exports."""
    path = tmp_path / "config.json"
    config = {"input_dir": "data/exports", "output_file": "out/report.json", "sla_hours": sla_hours}
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


@pytest.fixture
def make_record():
    """A factory: call it to get a valid raw record, with any fields overridden."""

    def _make_record(**overrides) -> dict:
        record = {
            "id": "INC-9001",
            "title": "Badge readers offline at the Zürich depot",
            "team": "it-support",
            "priority": "P2",
            "status": "open",
            "age_hours": 28,
            "assignee": None,
            "tags": ["access"],
        }
        record.update(overrides)
        return record

    return _make_record
