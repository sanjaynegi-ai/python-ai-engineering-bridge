"""Building and writing the report.

Workbook Milestone 5.
"""

from datetime import datetime
from pathlib import Path

from incident_api.models import Rejection, Report, Ticket


def build_report(
    tickets: list[Ticket],
    rejections: list[Rejection],
    *,
    sla_hours: dict[str, int],
    generated_at: datetime,
) -> Report:
    """Build the Report model: the same content as Project 01, as Pydantic models.

    Drop the microseconds from generated_at.
    """
    raise NotImplementedError


def write_report(report: Report, path: Path, *, include_rejected: bool = True) -> None:
    """Write the report as indented (2 spaces) UTF-8 JSON, creating missing folders.

    With include_rejected=False, leave the "rejected" key out entirely.
    """
    raise NotImplementedError
