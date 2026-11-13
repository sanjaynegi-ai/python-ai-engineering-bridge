"""Reading incident reports from a JSON Lines file: one JSON object per line."""

from pathlib import Path

from pydantic import ValidationError

from incident_triage.errors import ReportFileError
from incident_triage.models import IncidentReport


def load_reports(path: Path) -> list[IncidentReport]:
    """Every report in the file, in order. Blank lines are skipped; any bad line is an error."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise ReportFileError(f"{path}: file not found") from error
    except UnicodeDecodeError as error:
        raise ReportFileError(f"{path}: not UTF-8 text") from error

    reports = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            reports.append(IncidentReport.model_validate_json(line))
        except ValidationError as error:
            first = error.errors(include_url=False)[0]
            raise ReportFileError(f"{path.name} line {number}: {first['msg']}") from error
    return reports
