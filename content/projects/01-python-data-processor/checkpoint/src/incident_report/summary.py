"""Calculations over cleaned tickets."""

from collections import Counter

from incident_report.models import Ticket


def deduplicate(tickets: list[Ticket]) -> list[Ticket]:
    """Keep the first ticket for each id, in input order."""
    seen_ids = set()
    unique = []
    for ticket in tickets:
        if ticket.id not in seen_ids:
            seen_ids.add(ticket.id)
            unique.append(ticket)
    return unique


def breaches(tickets: list[Ticket], sla_hours: dict[str, int]) -> list[Ticket]:
    """Open tickets older than their SLA, oldest first."""
    breached = [ticket for ticket in tickets if ticket.is_breached(sla_hours)]
    return sorted(breached, key=lambda ticket: ticket.age_hours, reverse=True)


def team_summary(tickets: list[Ticket], sla_hours: dict[str, int]) -> dict[str, dict]:
    """Per-team counts of open, breached and unassigned tickets, and the oldest open age."""
    open_by_team: dict[str, list[Ticket]] = {ticket.team: [] for ticket in tickets}
    for ticket in tickets:
        if ticket.is_open:
            open_by_team[ticket.team].append(ticket)
    return {
        team: {
            "open": len(open_tickets),
            "breached": sum(ticket.is_breached(sla_hours) for ticket in open_tickets),
            "unassigned_open": sum(ticket.assignee is None for ticket in open_tickets),
            "oldest_open_hours": max((t.age_hours for t in open_tickets), default=None),
        }
        for team, open_tickets in open_by_team.items()
    }


def top_tags(tickets: list[Ticket], n: int) -> list[tuple[str, int]]:
    """The n most common tags: highest count first, ties alphabetical."""
    counts = Counter(tag for ticket in tickets for tag in ticket.tags)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]
