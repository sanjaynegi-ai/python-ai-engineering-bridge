"""Acceptance tests for the command line (workbook Milestone 5). Do not edit."""

import json
import shutil
from pathlib import Path

import pytest

from incident_triage.cli import main

SAMPLE = Path(__file__).parents[2] / "data" / "reports.jsonl"


@pytest.fixture
def reports_file(clean_env, tmp_path) -> Path:
    target = tmp_path / "reports.jsonl"
    shutil.copy(SAMPLE, target)
    return target


def test_offline_run_triages_every_sample_report(reports_file, tmp_path, capsys):
    out = tmp_path / "out" / "triage.json"

    code = main([str(reports_file), "--offline", "--out", str(out)])

    assert code == 0
    run = json.loads(out.read_text(encoding="utf-8"))
    assert len(run["outcomes"]) == 12
    assert run["outcomes"][0]["report_id"] == "RPT-1001"
    assert run["cost_usd"] is None
    assert "12 of 12 triaged" in capsys.readouterr().out


def test_missing_key_is_a_clear_error(reports_file, capsys):
    code = main([str(reports_file)])

    captured = capsys.readouterr()
    assert code == 2
    assert "OPENAI_API_KEY is not set" in captured.err
    assert "Traceback" not in captured.err


def test_missing_reports_file(clean_env, tmp_path, capsys):
    code = main([str(tmp_path / "nope.jsonl"), "--offline"])

    assert code == 2
    assert "file not found" in capsys.readouterr().err


def test_invalid_line_is_reported_with_its_number(clean_env, tmp_path, capsys):
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"id": "RPT-1", "text": "ok"}\n{"id": "oops", "text": "x"}\n', encoding="utf-8"
    )

    code = main([str(path), "--offline"])

    assert code == 2
    assert "line 2" in capsys.readouterr().err


def test_sample_data_contains_the_tricky_reports():
    lines = [json.loads(line) for line in SAMPLE.read_text(encoding="utf-8").splitlines() if line]

    texts = {line["id"]: line["text"] for line in lines}
    assert "Ignore your previous instructions" in texts["RPT-1010"]
    assert texts["RPT-1009"].startswith("Le portail")
