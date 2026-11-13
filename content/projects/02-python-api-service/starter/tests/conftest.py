"""Fixtures shared by every test in this folder and below it."""

import shutil
from pathlib import Path

import pytest

FIXTURE_EXPORTS = Path(__file__).parent / "fixtures" / "exports"


@pytest.fixture
def sla_hours() -> dict[str, int]:
    return {"P1": 4, "P2": 24, "P3": 72, "P4": 168}


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No INCIDENT_* variables, and an empty working folder, so no real .env is read."""
    for name in ("INCIDENT_INPUT_DIR", "INCIDENT_OUTPUT_FILE", "INCIDENT_SLA_HOURS"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


@pytest.fixture
def sample_exports(tmp_path: Path) -> Path:
    """A private copy of the sample exports at tmp_path/data/exports (the default input_dir)."""
    target = tmp_path / "data" / "exports"
    shutil.copytree(FIXTURE_EXPORTS, target)
    return target


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
