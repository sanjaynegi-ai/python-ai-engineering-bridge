"""Unit tests for summary edge cases."""

from incident_report.models import Ticket
from incident_report.summary import breaches, deduplicate, team_summary, top_tags


def make_ticket(ticket_id: str, **changes) -> Ticket:
    fields = {
        "id": ticket_id,
        "title": "Synthetic ticket",
        "team": "platform",
        "priority": "P1",
        "status": "open",
        "age_hours": 1,
    }
    fields.update(changes)
    return Ticket(**fields)


def test_deduplicate_empty_list():
    assert deduplicate([]) == []


def test_deduplicate_does_not_change_its_input():
    tickets = [make_ticket("INC-1"), make_ticket("INC-1")]

    deduplicate(tickets)

    assert len(tickets) == 2


def test_breaches_empty_when_nothing_is_late(sla_hours):
    assert breaches([make_ticket("INC-1", age_hours=4)], sla_hours) == []


def test_team_summary_counts_only_open_unassigned(sla_hours):
    tickets = [
        make_ticket("INC-1", assignee=None),
        make_ticket("INC-2", assignee=None, status="closed"),
        make_ticket("INC-3", assignee="li"),
    ]

    assert team_summary(tickets, sla_hours)["platform"]["unassigned_open"] == 1


def test_top_tags_with_fewer_tags_than_requested():
    assert top_tags([make_ticket("INC-1", tags=("dns",))], 5) == [("dns", 1)]


def test_top_tags_without_any_tags():
    assert top_tags([make_ticket("INC-1")], 3) == []
