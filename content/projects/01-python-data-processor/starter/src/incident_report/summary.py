"""Calculations over cleaned tickets.

Workbook Milestone 4: move your Session 02 functions here, and change them to
work with Ticket objects (ticket.team instead of ticket["team"]).
"""

from incident_report.models import Ticket


def deduplicate(tickets: list[Ticket]) -> list[Ticket]:
    """Keep the first ticket for each id, in input order."""
    raise NotImplementedError


def breaches(tickets: list[Ticket], sla_hours: dict[str, int]) -> list[Ticket]:
    """Open tickets older than their SLA, oldest first."""
    raise NotImplementedError


def team_summary(tickets: list[Ticket], sla_hours: dict[str, int]) -> dict[str, dict]:
    """Per-team stats, with the same keys as Session 02's team_summary."""
    raise NotImplementedError


def top_tags(tickets: list[Ticket], n: int) -> list[tuple[str, int]]:
    """The n most common tags: highest count first, ties alphabetical."""
    raise NotImplementedError
