"""Morning incident summary for the Orbital Logistics on-call lead.

Implement each function so that `uv run check_summary.py` passes, then make
`main()` print the report described in the workbook.

Ground rule for every function: never modify the tickets you are given.
Build and return new lists and dicts instead.
"""

from sample_tickets import CLOSED_STATUSES, SLA_HOURS, TICKETS


def normalise_ticket(ticket: dict) -> dict:
    """Return a cleaned COPY of one ticket.

    - "team" and "status": surrounding whitespace removed, lower case.
    - "assignee": surrounding whitespace removed; blank or missing becomes None.
    - "tags": lower case, duplicates removed, sorted alphabetically.
    - Every other field is copied unchanged.
    """
    raise NotImplementedError


def deduplicate(tickets: list[dict]) -> list[dict]:
    """Return the tickets with repeated IDs removed, keeping the FIRST occurrence.

    The order of the remaining tickets must match the input order.
    """
    raise NotImplementedError


def is_open(ticket: dict) -> bool:
    """Return True unless the (normalised) status is in CLOSED_STATUSES."""
    raise NotImplementedError


def is_breached(ticket: dict, sla_hours: dict[str, int]) -> bool:
    """Return True if the ticket is open AND older than the SLA for its priority."""
    raise NotImplementedError


def count_by(tickets: list[dict], field: str) -> dict[str, int]:
    """Return how many tickets have each value of `field`, e.g. {"P1": 3, "P2": 5}."""
    raise NotImplementedError


def group_by_team(tickets: list[dict]) -> dict[str, list[str]]:
    """Return {team: [ticket ids]}, with the ids in input order."""
    raise NotImplementedError


def team_summary(tickets: list[dict], sla_hours: dict[str, int]) -> dict[str, dict]:
    """Return one stats dict per team that appears in `tickets`.

    Each value has exactly these keys:
      "open":              number of open tickets
      "breached":          number of open tickets that breached their SLA
      "unassigned_open":   number of open tickets with no assignee
      "oldest_open_hours": age of the oldest open ticket, or None if none are open
    """
    raise NotImplementedError


def top_tags(tickets: list[dict], n: int) -> list[tuple[str, int]]:
    """Return the n most common tags as (tag, count) pairs.

    Order: highest count first; ties broken alphabetically by tag.
    """
    raise NotImplementedError


def main() -> None:
    """Print the morning summary (see Milestone 7 in the workbook)."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
