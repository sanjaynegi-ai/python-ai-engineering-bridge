"""Acceptance tests for the command-line entry points. Do not edit."""

import json
import shutil
import subprocess
import sys

from incident_report.cli import main


def test_main_with_sample_data(config_file, capsys):
    exit_code = main([str(config_file)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "tickets-legacy.json" in captured.err
    report_path = config_file.parent / "out" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["unique_tickets"] == 10


def test_main_with_only_valid_data(config_file, sample_exports):
    for path in sample_exports.glob("*.json"):
        if path.name != "tickets-2026-10-19.json":
            path.unlink()

    assert main([str(config_file)]) == 0


def test_main_with_missing_config(tmp_path, capsys):
    exit_code = main([str(tmp_path / "missing.json")])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.startswith("error:")
    assert "Traceback" not in captured.out + captured.err


def test_main_with_no_export_files(config_file, sample_exports):
    shutil.rmtree(sample_exports)
    sample_exports.mkdir()

    assert main([str(config_file)]) == 2


def test_python_dash_m_runs_the_package(config_file):
    result = subprocess.run(
        [sys.executable, "-m", "incident_report", str(config_file)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1, result.stderr
    assert "Report written to" in result.stdout
