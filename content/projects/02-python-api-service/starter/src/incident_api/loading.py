"""Reading export files and turning their records into Tickets or Rejections."""

import json
from pathlib import Path

from incident_api.errors import ExportError
from incident_api.models import Rejection, Ticket


def read_export(path: Path) -> list:
    """Return the top-level list of one export file, without validating its records."""
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise ExportError(f"{path.name}: file not found") from error
    except UnicodeDecodeError as error:
        raise ExportError(f"{path.name}: not UTF-8 text") from error
    except json.JSONDecodeError as error:
        raise ExportError(
            f"{path.name}: invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(data, list):
        raise ExportError(f"{path.name}: expected a list of tickets, got {type(data).__name__}")
    return data


def load_exports(paths: list[Path]) -> tuple[list[Ticket], list[Rejection]]:
    """Validate every record of every export, in order. Nothing stops the run.

    Workbook Milestone 4. A file that raises ExportError becomes one Rejection with
    the error message as its only problem; an invalid record becomes a Rejection
    built by Rejection.from_validation_error.
    """
    raise NotImplementedError
