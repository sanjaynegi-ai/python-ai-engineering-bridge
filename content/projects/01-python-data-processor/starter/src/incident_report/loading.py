"""Reading configuration and export files, and validating raw records.

Workbook Milestone 3: move your Session 03 code here, and adapt it so that
load_config returns a Config and load_exports returns Tickets and Rejections.
"""

from pathlib import Path

from incident_report.models import Config, Rejection, Ticket

# The type each field of a raw ticket record must have. A tuple means "any of these".
FIELD_TYPES = {
    "id": str,
    "title": str,
    "team": str,
    "priority": str,
    "status": str,
    "age_hours": int,
    "assignee": (str, type(None)),
    "tags": list,
}


def load_config(path: Path) -> Config:
    """Read the JSON configuration; paths are relative to the config file's folder.

    Same rules and ConfigError cases as Session 03's load_config.
    """
    raise NotImplementedError


def read_export(path: Path) -> list:
    """Return the top-level list of one export file, without validating its records.

    Same rules and ExportError cases as Session 03's read_export.
    """
    raise NotImplementedError


def validate_record(record: object, *, sla_hours: dict[str, int]) -> list[str]:
    """Return every problem with one raw record. An empty list means it is valid.

    This is Session 03's validate_ticket, renamed: it checks raw records, before
    they become Ticket objects. The messages and their order are unchanged.
    """
    raise NotImplementedError


def load_exports(
    paths: list[Path], *, sla_hours: dict[str, int]
) -> tuple[list[Ticket], list[Rejection]]:
    """Read and validate every export, in order.

    Valid records become Tickets (via Ticket.from_record). A file that raises
    ExportError becomes one Rejection with record and id set to None; an invalid
    record becomes a Rejection with its index and id. Processing always continues.
    """
    raise NotImplementedError
