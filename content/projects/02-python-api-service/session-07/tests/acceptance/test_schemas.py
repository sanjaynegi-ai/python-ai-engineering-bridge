"""Acceptance tests for the API schemas (workbook Milestone 3). Do not edit."""

import pytest
from pydantic import ValidationError

from incident_api.models import Ticket
from incident_api.schemas import Health, TicketFilters, TicketOut, TicketPage


def test_ticket_out_adds_derived_fields(make_record, sla_hours):
    ticket = Ticket.model_validate(make_record(age_hours=28, priority="P2", tags=["VPN", "dns"]))

    out = TicketOut.from_ticket(ticket, sla_hours=sla_hours)

    assert out.model_dump() == {
        "id": "INC-9001",
        "title": "Badge readers offline at the Zürich depot",
        "team": "it-support",
        "priority": "P2",
        "status": "open",
        "age_hours": 28,
        "assignee": None,
        "tags": ["dns", "vpn"],
        "is_open": True,
        "breached": True,
        "sla_hours": 24,
    }


def test_ticket_out_for_a_resolved_ticket(make_record, sla_hours):
    ticket = Ticket.model_validate(make_record(status="Resolved", age_hours=500))

    out = TicketOut.from_ticket(ticket, sla_hours=sla_hours)

    assert (out.is_open, out.breached) == (False, False)


def test_ticket_out_json_has_tags_as_a_list(make_record, sla_hours):
    out = TicketOut.from_ticket(Ticket.model_validate(make_record()), sla_hours=sla_hours)

    assert '"tags":["access"]' in out.model_dump_json()


def test_filters_defaults():
    assert TicketFilters().model_dump() == {
        "team": None,
        "priority": None,
        "open_only": False,
        "limit": 20,
        "offset": 0,
    }


@pytest.mark.parametrize(
    "data",
    [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"priority": "P9"}, {"colour": "blue"}],
)
def test_filters_reject_invalid_values(data):
    with pytest.raises(ValidationError):
        TicketFilters.model_validate(data)


def test_filters_convert_query_string_text():
    filters = TicketFilters.model_validate({"limit": "5", "open_only": "true"})

    assert (filters.limit, filters.open_only) == (5, True)


def test_page_and_health_shapes():
    page = TicketPage(total=0, limit=20, offset=0, items=[])
    health = Health(tickets=10, rejected=6)

    assert page.model_dump() == {"total": 0, "limit": 20, "offset": 0, "items": []}
    assert health.model_dump() == {"status": "ok", "tickets": 10, "rejected": 6}
