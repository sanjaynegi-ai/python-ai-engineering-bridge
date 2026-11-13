"""Nightly incident report for Orbital Logistics (fictional).

Reads every ticket export in a folder, validates the records, and writes a JSON
report. Bad files and bad records are reported, never allowed to stop the run.

Implement each function so that `uv run check_report.py` passes. The functions
you wrote in Session 02 live in ticket_summary.py, and build_report uses them.

Usage:
    uv run incident_report.py [CONFIG_PATH]     (default: config.json)

Exit codes:
    0  report written, no records or files rejected
    1  report written, but some records or files were rejected
    2  the report could not be produced (bad configuration, no export files)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from ticket_summary import (
    deduplicate,
    is_breached,
    is_open,
    normalise_ticket,
    team_summary,
    top_tags,
)

# The type each field of a ticket record must have. A tuple means "any of these".
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


class ConfigError(Exception):
    """The configuration file is missing or invalid."""


class ExportError(Exception):
    """An export file cannot be read, or is not a JSON list."""


def load_config(path: Path) -> dict:
    """Read and check the JSON configuration file.

    Returns a dict with exactly these keys:
      "input_dir":   Path, resolved relative to the config file's folder
      "output_file": Path, resolved relative to the config file's folder
      "sla_hours":   dict mapping each priority (str) to hours (int, greater than 0)

    Raises ConfigError, with a message that includes the file name, when:
      - the file does not exist                  (chain the FileNotFoundError)
      - the file is not valid JSON               (chain the JSONDecodeError)
      - the top level is not a JSON object
      - "input_dir", "output_file" or "sla_hours" is missing (name the key)
      - "input_dir" or "output_file" is not a string
      - "sla_hours" is not an object of positive integers
    """
    raise NotImplementedError


def read_export(path: Path) -> list:
    """Read one export file and return its top-level list, without validating records.

    Raises ExportError, with a message that starts with the file name, when:
      - the file does not exist                  (chain the FileNotFoundError)
      - the file is not UTF-8 text               (chain the UnicodeDecodeError)
      - the file is not valid JSON               (chain the JSONDecodeError, and
                                                  include its line number as "line N")
      - the top level is not a list
    """
    raise NotImplementedError


def validate_ticket(record: object, *, sla_hours: dict[str, int]) -> list[str]:
    """Return every problem with one record, as a list of messages. [] means valid.

    If the record is not a dict, return exactly ["record is not a JSON object"].

    Otherwise, first one message per field in FIELD_TYPES order, where needed:
      missing field 'id'
      field 'age_hours' must be int, got str    (booleans are NOT accepted as int)
      field 'assignee' must be str or None, got int
    then these value checks, in this order:
      field 'age_hours' must not be negative    (only if age_hours is an int)
      unknown priority 'P9'                     (only if priority is a str)
      field 'tags' must contain only strings    (only if tags is a list)
    """
    raise NotImplementedError


def load_exports(paths: list[Path], *, sla_hours: dict[str, int]) -> tuple[list, list]:
    """Read and validate every export, in the given order.

    Returns (valid_records, rejected). Each rejected entry is a dict:
      {"file": file name, "record": index in the file or None,
       "id": the record's id or None, "problems": [messages]}

    A file that raises ExportError becomes ONE rejected entry, with "record" and
    "id" set to None and the error message as its only problem. Processing then
    continues with the next file.
    """
    raise NotImplementedError


def build_report(
    tickets: list[dict],
    rejected: list[dict],
    *,
    sla_hours: dict[str, int],
    generated_at: datetime,
) -> dict:
    """Build the JSON-ready report from valid records (see the workbook for the shape)."""
    raise NotImplementedError


def write_report(report: dict, path: Path) -> None:
    """Write the report as UTF-8 JSON, creating any missing folders.

    Use an indent of 2, and write non-ASCII characters as they are ("Zürich",
    not "Z\\u00fcrich").
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Run the whole job and return the exit code described at the top of this file."""
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
