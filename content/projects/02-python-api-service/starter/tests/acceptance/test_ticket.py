"""Acceptance tests for the Ticket model (workbook Milestone 2). Do not edit."""

import pytest
from pydantic import ValidationError

from incident_api.models import Ticket


def failing_fields(error: ValidationError) -> list[str]:
    """The field names Pydantic complained about, in order."""
    return [".".join(str(part) for part in issue["loc"]) for issue in error.errors()]


def test_valid_record_is_normalised(make_record):
    ticket = Ticket.model_validate(
        make_record(
            team="  IT-Support ",
            status="OPEN",
            assignee="  ",
            tags=["Network", "vpn", "network"],
        )
    )

    assert ticket.team == "it-support"
    assert ticket.status == "open"
    assert ticket.assignee is None
    assert ticket.tags == ("network", "vpn")


@pytest.mark.parametrize(
    ("raw", "expected"), [(None, None), ("", None), ("   ", None), (" amira ", "amira")]
)
def test_assignee(make_record, raw, expected):
    assert Ticket.model_validate(make_record(assignee=raw)).assignee == expected


def test_unknown_fields_are_ignored(make_record):
    ticket = Ticket.model_validate(make_record(escalated=True))

    assert not hasattr(ticket, "escalated")


def test_ticket_is_frozen(make_record):
    ticket = Ticket.model_validate(make_record())

    with pytest.raises(ValidationError):
        ticket.status = "closed"


@pytest.mark.parametrize(
    ("changes", "fields"),
    [
        ({"age_hours": "12"}, ["age_hours"]),
        ({"age_hours": True}, ["age_hours"]),
        ({"age_hours": -3}, ["age_hours"]),
        ({"age_hours": 12.5}, ["age_hours"]),
        ({"priority": "P9"}, ["priority"]),
        ({"tags": "network"}, ["tags"]),
        ({"tags": ["dns", 4]}, ["tags.1"]),
        ({"assignee": 7}, ["assignee"]),
        ({"id": "3004"}, ["id"]),
        ({"title": ""}, ["title"]),
        ({"priority": "P9", "age_hours": "x"}, ["priority", "age_hours"]),
    ],
    ids=[
        "age-string",
        "age-bool",
        "age-negative",
        "age-fraction",
        "priority-unknown",
        "tags-string",
        "tag-not-string",
        "assignee-number",
        "id-pattern",
        "title-empty",
        "two-problems",
    ],
)
def test_invalid_records(make_record, changes, fields):
    with pytest.raises(ValidationError) as caught:
        Ticket.model_validate(make_record(**changes))

    assert failing_fields(caught.value) == fields


@pytest.mark.parametrize("field", ["id", "assignee", "tags", "age_hours"])
def test_required_fields(make_record, field):
    record = make_record()
    del record[field]

    with pytest.raises(ValidationError) as caught:
        Ticket.model_validate(record)

    assert failing_fields(caught.value) == [field]


@pytest.mark.parametrize(
    ("status", "age_hours", "is_open", "is_breached"),
    [("open", 25, True, True), ("open", 24, True, False), ("closed", 500, False, False)],
)
def test_open_and_breached(make_record, sla_hours, status, age_hours, is_open, is_breached):
    ticket = Ticket.model_validate(make_record(status=status, age_hours=age_hours))

    assert ticket.is_open is is_open
    assert ticket.is_breached(sla_hours) is is_breached
