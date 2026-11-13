"""Building and writing the JSON report.

Workbook Milestone 5: move your Session 03 build_report and write_report here.
"""

from datetime import datetime
from pathlib import Path

from incident_report.models import Rejection, Ticket


def build_report(
    tickets: list[Ticket],
    rejections: list[Rejection],
    *,
    sla_hours: dict[str, int],
    generated_at: datetime,
) -> dict:
    """Build the JSON-ready report, in the same shape as Session 03.

    `tickets` are already normalised Ticket objects, but may contain duplicates.
    """
    raise NotImplementedError


def write_report(report: dict, path: Path) -> None:
    """Write the report as indented UTF-8 JSON, creating missing folders."""
    raise NotImplementedError
