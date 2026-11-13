"""Acceptance tests for incident_report.models. Do not edit."""

import dataclasses

import pytest

from incident_report.models import Config, Rejection, Ticket


def test_from_record_normalises(make_record):
    record = make_record(
        team="  IT-Support ", status="OPEN", assignee="  ", tags=["Network", "vpn", "network"]
    )

    ticket = Ticket.from_record(record)

    assert ticket == Ticket(
        id="INC-9001",
        title="Badge readers offline at the Zürich depot",
        team="it-support",
        priority="P2",
        status="open",
        age_hours=28,
        assignee=None,
        tags=("network", "vpn"),
    )


def test_from_record_does_not_change_the_record(make_record):
    record = make_record(team=" Platform ")

    Ticket.from_record(record)

    assert record == make_record(team=" Platform ")


def test_ticket_is_frozen(make_record):
    ticket = Ticket.from_record(make_record())

    with pytest.raises(dataclasses.FrozenInstanceError):
        ticket.status = "closed"


def test_ticket_defaults():
    ticket = Ticket(
        id="INC-1", title="t", team="platform", priority="P1", status="open", age_hours=1
    )

    assert ticket.assignee is None
    assert ticket.tags == ()


@pytest.mark.parametrize(
    ("status", "expected"),
    [("open", True), ("in_progress", True), ("resolved", False), ("closed", False)],
)
def test_is_open(make_record, status, expected):
    assert Ticket.from_record(make_record(status=status)).is_open is expected


@pytest.mark.parametrize(
    ("status", "age_hours", "expected"),
    [
        ("open", 25, True),
        ("open", 24, False),  # exactly at the limit is not a breach
        ("closed", 500, False),  # closed tickets never breach
    ],
)
def test_is_breached(make_record, sla_hours, status, age_hours, expected):
    ticket = Ticket.from_record(make_record(status=status, age_hours=age_hours, priority="P2"))

    assert ticket.is_breached(sla_hours) is expected


def test_rejection_to_dict():
    rejection = Rejection(file="a.json", record=3, id="INC-1", problems=("bad", "worse"))

    assert rejection.to_dict() == {
        "file": "a.json",
        "record": 3,
        "id": "INC-1",
        "problems": ["bad", "worse"],
    }


def test_config_fields():
    names = [field.name for field in dataclasses.fields(Config)]

    assert names == ["input_dir", "output_file", "sla_hours"]
