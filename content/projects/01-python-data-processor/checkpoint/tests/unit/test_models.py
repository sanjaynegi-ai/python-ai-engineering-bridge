"""Unit tests for Ticket edge cases not covered by the acceptance tests."""

import pytest

from incident_report.models import Ticket


@pytest.mark.parametrize(
    ("raw_assignee", "expected"),
    [(None, None), ("", None), ("   ", None), (" amira ", "amira"), ("li", "li")],
)
def test_assignee_normalisation(make_record, raw_assignee, expected):
    assert Ticket.from_record(make_record(assignee=raw_assignee)).assignee == expected


def test_tags_become_a_sorted_unique_tuple(make_record):
    ticket = Ticket.from_record(make_record(tags=["VPN", "dns", "vpn", "Dns"]))

    assert ticket.tags == ("dns", "vpn")


def test_empty_tags(make_record):
    assert Ticket.from_record(make_record(tags=[])).tags == ()


def test_tickets_with_equal_fields_are_equal(make_record):
    assert Ticket.from_record(make_record()) == Ticket.from_record(make_record())


def test_unknown_priority_raises_key_error(make_record):
    ticket = Ticket.from_record(make_record(priority="P9"))

    with pytest.raises(KeyError):
        ticket.is_breached({"P1": 4})
