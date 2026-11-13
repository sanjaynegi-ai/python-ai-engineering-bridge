"""Acceptance tests for TicketService and its exceptions (workbook Milestone 2). Do not edit."""

from datetime import UTC, datetime

import pytest

from incident_api.errors import DuplicateTicketError, TicketNotFoundError
from incident_api.models import Ticket
from incident_api.service import TicketService


@pytest.fixture
def service(sample_exports, sla_hours) -> TicketService:
    return TicketService.from_exports(sorted(sample_exports.glob("*.json")), sla_hours=sla_hours)


def test_counts_unique_tickets_and_rejections(service):
    assert service.ticket_count == 10
    assert service.rejection_count == 6


def test_get_returns_the_first_record_of_a_duplicated_id(service):
    ticket = service.get("INC-3004")

    assert isinstance(ticket, Ticket)
    assert ticket.age_hours == 80


def test_get_unknown_id_raises_ticket_not_found(service):
    with pytest.raises(TicketNotFoundError) as caught:
        service.get("INC-9999")

    assert caught.value.ticket_id == "INC-9999"
    assert str(caught.value) == "ticket INC-9999 not found"


def test_find_without_filters_returns_unique_tickets_in_load_order(service):
    ids = [ticket.id for ticket in service.find()]

    assert ids == [f"INC-{n}" for n in range(3001, 3011)]


def test_find_by_team_ignores_case_and_spaces(service):
    ids = [ticket.id for ticket in service.find(team="  Database ")]

    assert ids == ["INC-3002", "INC-3004", "INC-3008", "INC-3010"]


def test_find_by_priority(service):
    assert [ticket.id for ticket in service.find(priority="P1")] == ["INC-3001", "INC-3008"]


def test_find_open_only_excludes_resolved_and_closed(service):
    ids = [ticket.id for ticket in service.find(open_only=True)]

    assert "INC-3005" not in ids
    assert len(ids) == 9


def test_find_combines_filters(service):
    found = service.find(team="platform", priority="P2", open_only=True)

    assert [ticket.id for ticket in found] == ["INC-3006"]


def test_find_unknown_team_returns_empty_list(service):
    assert service.find(team="facilities") == []


def test_add_stores_a_new_ticket(service, make_record):
    ticket = Ticket.model_validate(make_record(id="INC-9001"))

    assert service.add(ticket) is ticket
    assert service.get("INC-9001") == ticket
    assert service.ticket_count == 11
    assert service.find()[-1].id == "INC-9001"


def test_add_existing_id_raises_duplicate_and_keeps_the_original(service, make_record):
    with pytest.raises(DuplicateTicketError) as caught:
        service.add(Ticket.model_validate(make_record(id="INC-3001")))

    assert str(caught.value) == "ticket INC-3001 already exists"
    assert caught.value.ticket_id == "INC-3001"
    assert service.get("INC-3001").team == "platform"
    assert service.ticket_count == 10


def test_is_breached_uses_the_service_sla(service):
    assert service.is_breached(service.get("INC-3007")) is True
    assert service.is_breached(service.get("INC-3008")) is False


def test_report_matches_the_cli_report(service):
    report = service.report(generated_at=datetime(2026, 10, 22, 2, 0, tzinfo=UTC))

    assert report.totals.model_dump() == {
        "valid_records": 11,
        "unique_tickets": 10,
        "open": 9,
        "breached": 6,
        "rejected": 6,
    }
    assert len(report.rejected) == 6


def test_report_includes_added_tickets(service, make_record):
    service.add(Ticket.model_validate(make_record(id="INC-9001", age_hours=99, priority="P2")))

    totals = service.report(generated_at=datetime(2026, 10, 22, 2, 0, tzinfo=UTC)).totals

    assert (totals.valid_records, totals.unique_tickets, totals.breached) == (12, 11, 7)


def test_service_can_be_built_directly_from_tickets(make_record, sla_hours):
    tickets = [Ticket.model_validate(make_record(id=f"INC-{n}")) for n in (1, 2, 1)]

    service = TicketService(tickets, [], sla_hours=sla_hours)

    assert service.ticket_count == 2
    assert service.rejection_count == 0
    assert service.sla_hours == sla_hours
