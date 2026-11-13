"""Building and writing the JSON report."""

import json
from datetime import datetime
from pathlib import Path

from incident_report.models import Rejection, Ticket
from incident_report.summary import breaches, deduplicate, team_summary, top_tags


def build_report(
    tickets: list[Ticket],
    rejections: list[Rejection],
    *,
    sla_hours: dict[str, int],
    generated_at: datetime,
) -> dict:
    """Build the JSON-ready report from valid tickets and the rejections."""
    unique = deduplicate(tickets)
    open_tickets = [ticket for ticket in unique if ticket.is_open]
    breached = breaches(unique, sla_hours)
    return {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "totals": {
            "valid_records": len(tickets),
            "unique_tickets": len(unique),
            "open": len(open_tickets),
            "breached": len(breached),
            "rejected": len(rejections),
        },
        "teams": team_summary(unique, sla_hours),
        "breaches": [
            {
                "id": ticket.id,
                "title": ticket.title,
                "team": ticket.team,
                "priority": ticket.priority,
                "age_hours": ticket.age_hours,
                "sla_hours": sla_hours[ticket.priority],
            }
            for ticket in breached
        ],
        "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags(open_tickets, 3)],
        "rejected": [rejection.to_dict() for rejection in rejections],
    }


def write_report(report: dict, path: Path) -> None:
    """Write the report as indented UTF-8 JSON, creating missing folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
