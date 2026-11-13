"""Acceptance tests for the report models and report.py (workbook Milestone 5). Do not edit."""

import json
from datetime import UTC, datetime

import pytest

from incident_api.loading import load_exports
from incident_api.models import Report, TagCount, Totals
from incident_api.report import build_report, write_report

GENERATED_AT = datetime(2026, 10, 21, 2, 0, 0, 123456, tzinfo=UTC)


@pytest.fixture
def loaded(sample_exports):
    return load_exports(sorted(sample_exports.glob("*.json")))


def test_report_json_round_trip():
    report = Report(
        generated_at=datetime(2026, 10, 21, 2, 0, tzinfo=UTC),
        totals=Totals(valid_records=1, unique_tickets=1, open=1, breached=0, rejected=0),
        teams={},
        breaches=[],
        top_tags=[TagCount(tag="dns", count=1)],
        rejected=[],
    )

    text = report.model_dump_json()

    assert '"generated_at":"2026-10-21T02:00:00Z"' in text
    assert Report.model_validate_json(text) == report


@pytest.fixture
def report(loaded, sla_hours) -> Report:
    tickets, rejections = loaded
    return build_report(tickets, rejections, sla_hours=sla_hours, generated_at=GENERATED_AT)


def test_report_totals_and_sections(report):
    assert report.totals.model_dump() == {
        "valid_records": 11,
        "unique_tickets": 10,
        "open": 9,
        "breached": 6,
        "rejected": 6,
    }
    assert report.teams["it-support"].model_dump() == {
        "open": 2,
        "breached": 2,
        "unassigned_open": 2,
        "oldest_open_hours": 200,
    }
    assert [b.id for b in report.breaches] == [
        "INC-3007",
        "INC-3004",
        "INC-3002",
        "INC-3009",
        "INC-3006",
        "INC-3001",
    ]
    assert report.breaches[3].model_dump() == {
        "id": "INC-3009",
        "title": "Badge readers offline at the Zürich depot",
        "team": "it-support",
        "priority": "P2",
        "age_hours": 28,
        "sla_hours": 24,
    }
    assert [(t.tag, t.count) for t in report.top_tags] == [
        ("latency", 3),
        ("network", 3),
        ("api", 2),
    ]


def test_report_drops_microseconds(report):
    assert report.generated_at == datetime(2026, 10, 21, 2, 0, tzinfo=UTC)


def test_write_report(report, tmp_path):
    path = tmp_path / "nested" / "report.json"

    write_report(report, path)

    text = path.read_text(encoding="utf-8")
    assert "Zürich" in text
    assert text.splitlines()[1].startswith('  "')
    data = json.loads(text)
    assert data["generated_at"] == "2026-10-21T02:00:00Z"
    assert len(data["rejected"]) == 6
    assert Report.model_validate(data) == report


def test_write_report_without_rejections(report, tmp_path):
    path = tmp_path / "summary.json"

    write_report(report, path, include_rejected=False)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert "rejected" not in data
    assert data["totals"]["rejected"] == 6
