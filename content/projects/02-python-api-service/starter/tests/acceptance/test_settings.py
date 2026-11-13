"""Acceptance tests for incident_api.settings. Do not edit."""

from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsError

from incident_api.settings import Settings


def test_defaults(clean_env):
    settings = Settings()

    assert settings.input_dir == Path("data/exports")
    assert settings.output_file == Path("out/report.json")
    assert settings.sla_hours == {"P1": 4, "P2": 24, "P3": 72, "P4": 168}


def test_environment_variables(clean_env):
    clean_env.setenv("INCIDENT_INPUT_DIR", "exports")
    clean_env.setenv("INCIDENT_SLA_HOURS", '{"P1": 2, "P2": 12, "P3": 48, "P4": 96}')

    settings = Settings()

    assert settings.input_dir == Path("exports")
    assert settings.sla_hours["P1"] == 2


def test_dotenv_file_in_the_working_folder(clean_env, tmp_path):
    (tmp_path / ".env").write_text("INCIDENT_OUTPUT_FILE=reports/today.json\n", encoding="utf-8")

    assert Settings().output_file == Path("reports/today.json")


def test_environment_wins_over_dotenv(clean_env, tmp_path):
    (tmp_path / ".env").write_text("INCIDENT_INPUT_DIR=from-dotenv\n", encoding="utf-8")
    clean_env.setenv("INCIDENT_INPUT_DIR", "from-environment")

    assert Settings().input_dir == Path("from-environment")


@pytest.mark.parametrize(
    "sla_json",
    [
        '{"P1": 4, "P2": 24, "P3": 72}',
        '{"P1": 4, "P2": 24, "P3": 72, "P4": 168, "P5": 400}',
        '{"P1": 0, "P2": 24, "P3": 72, "P4": 168}',
        '{"P1": 4, "P2": "soon", "P3": 72, "P4": 168}',
        '{"P1": 30, "P2": 24, "P3": 72, "P4": 168}',
        '{"P1": 24, "P2": 24, "P3": 72, "P4": 168}',
    ],
    ids=["missing-p4", "unknown-p5", "zero", "not-a-number", "decreasing", "equal"],
)
def test_invalid_sla_hours(clean_env, sla_json):
    clean_env.setenv("INCIDENT_SLA_HOURS", sla_json)

    with pytest.raises(ValidationError):
        Settings()


def test_sla_hours_that_are_not_json(clean_env):
    clean_env.setenv("INCIDENT_SLA_HOURS", "P1=4, P2=24")

    with pytest.raises(SettingsError):  # parsing fails before validation starts
        Settings()


def test_settings_are_frozen(clean_env):
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.input_dir = Path("elsewhere")
