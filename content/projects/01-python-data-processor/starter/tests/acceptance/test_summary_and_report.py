"""Acceptance tests for incident_report.summary and incident_report.report. Do not edit."""

import copy
import json
from datetime import UTC, datetime

import pytest

from incident_report.loading import load_exports
from incident_report.models import Ticket
from incident_report.report import build_report, write_report
from incident_report.summary import breaches, deduplicate, team_summary, top_tags

GENERATED_AT = datetime(2026, 10, 21, 2, 0, tzinfo=UTC)


def ticket(ticket_id="INC-1", **changes):
    fields = {
        "id": ticket_id,
        "title": "Synthetic ticket",
        "team": "platform",
        "priority": "P2",
        "status": "open",
        "age_hours": 1,
        "assignee": None,
        "tags": (),
    }
    fields.update(changes)
    return Ticket(**fields)


@pytest.fixture
def sample_tickets(sample_exports, sla_hours):
    tickets, rejections = load_exports(sorted(sample_exports.glob("*.json")), sla_hours=sla_hours)
    return tickets, rejections


# ---------------------------------------------------------------- summary
def test_deduplicate_keeps_the_first_in_order():
    tickets = [ticket("INC-2", age_hours=5), ticket("INC-1"), ticket("INC-2", age_hours=9)]

    unique = deduplicate(tickets)

    assert [(t.id, t.age_hours) for t in unique] == [("INC-2", 5), ("INC-1", 1)]


def test_breaches_are_open_and_oldest_first(sla_hours):
    tickets = [
        ticket("INC-1", age_hours=30),
        ticket("INC-2", age_hours=90),
        ticket("INC-3", age_hours=200, status="closed"),
        ticket("INC-4", age_hours=10),
    ]

    assert [t.id for t in breaches(tickets, sla_hours)] == ["INC-2", "INC-1"]


def test_team_summary_sample(sample_tickets, sla_hours):
    tickets, _ = sample_tickets

    summary = team_summary(deduplicate(tickets), sla_hours)

    assert summary == {
        "platform": {"open": 2, "breached": 2, "unassigned_open": 1, "oldest_open_hours": 26},
        "database": {"open": 4, "breached": 2, "unassigned_open": 2, "oldest_open_hours": 80},
        "network": {"open": 1, "breached": 0, "unassigned_open": 0, "oldest_open_hours": 12},
        "it-support": {"open": 2, "breached": 2, "unassigned_open": 2, "oldest_open_hours": 200},
    }


def test_team_summary_with_nothing_open(sla_hours):
    summary = team_summary([ticket(status="closed")], sla_hours)

    assert summary == {
        "platform": {"open": 0, "breached": 0, "unassigned_open": 0, "oldest_open_hours": None}
    }


def test_top_tags_breaks_ties_alphabetically():
    tickets = [ticket(tags=("zeta",)), ticket(tags=("alpha", "zeta")), ticket(tags=("alpha",))]

    assert top_tags(tickets, 2) == [("alpha", 2), ("zeta", 2)]


# ---------------------------------------------------------------- report
def test_build_report_totals(sample_tickets, sla_hours):
    tickets, rejections = sample_tickets
    before = copy.deepcopy(tickets)

    report = build_report(tickets, rejections, sla_hours=sla_hours, generated_at=GENERATED_AT)

    assert report["generated_at"] == "2026-10-21T02:00:00+00:00"
    assert report["totals"] == {
        "valid_records": 11,
        "unique_tickets": 10,
        "open": 9,
        "breached": 6,
        "rejected": 6,
    }
    assert tickets == before


def test_build_report_sections(sample_tickets, sla_hours):
    tickets, rejections = sample_tickets

    report = build_report(tickets, rejections, sla_hours=sla_hours, generated_at=GENERATED_AT)

    assert [b["id"] for b in report["breaches"]] == [
        "INC-3007",
        "INC-3004",
        "INC-3002",
        "INC-3009",
        "INC-3006",
        "INC-3001",
    ]
    assert report["breaches"][3] == {
        "id": "INC-3009",
        "title": "Badge readers offline at the Zürich depot",
        "team": "it-support",
        "priority": "P2",
        "age_hours": 28,
        "sla_hours": 24,
    }
    assert report["top_tags"] == [
        {"tag": "latency", "count": 3},
        {"tag": "network", "count": 3},
        {"tag": "api", "count": 2},
    ]
    assert report["rejected"][4] == {
        "file": "tickets-2026-10-21.json",
        "record": None,
        "id": None,
        "problems": [
            "tickets-2026-10-21.json: invalid JSON at line 21, column 5: "
            "Expecting property name enclosed in double quotes"
        ],
    }
    assert json.loads(json.dumps(report)) == report  # only JSON types inside


def test_write_report(tmp_path):
    path = tmp_path / "nested" / "out" / "report.json"
    report = {"title": "Zürich depot", "counts": [1, 2]}

    write_report(report, path)

    text = path.read_text(encoding="utf-8")
    assert "Zürich" in text
    assert text.splitlines()[1].startswith('  "')
    assert json.loads(text) == report
