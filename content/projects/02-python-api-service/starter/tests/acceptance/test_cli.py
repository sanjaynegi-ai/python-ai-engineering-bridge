"""Acceptance tests for the command line (workbook Milestone 6). Do not edit."""

import json

from incident_api.cli import main


def test_cli_with_sample_data(clean_env, sample_exports, tmp_path, capsys):
    assert main([]) == 1

    captured = capsys.readouterr()
    assert "tickets-legacy.json" in captured.err
    data = json.loads((tmp_path / "out" / "report.json").read_text(encoding="utf-8"))
    assert data["totals"]["unique_tickets"] == 10


def test_cli_summary_only(clean_env, sample_exports, tmp_path):
    main(["--summary-only"])

    data = json.loads((tmp_path / "out" / "report.json").read_text(encoding="utf-8"))
    assert "rejected" not in data


def test_cli_only_valid_data(clean_env, sample_exports):
    for path in sample_exports.glob("*.json"):
        if path.name != "tickets-2026-10-19.json":
            path.unlink()

    assert main([]) == 0


def test_cli_invalid_settings(clean_env, sample_exports, capsys):
    clean_env.setenv("INCIDENT_SLA_HOURS", '{"P1": 30, "P2": 24, "P3": 72, "P4": 168}')

    assert main([]) == 2
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "sla_hours" in captured.err


def test_cli_settings_that_are_not_json(clean_env, sample_exports, capsys):
    clean_env.setenv("INCIDENT_SLA_HOURS", "P1=4, P2=24")

    assert main([]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_cli_no_exports(clean_env, tmp_path):
    (tmp_path / "data" / "exports").mkdir(parents=True)

    assert main([]) == 2
