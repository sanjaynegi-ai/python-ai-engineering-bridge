"""Command-line entry point: `incident-report [--summary-only]`.

Settings come from INCIDENT_* environment variables or .env (see .env.example).

Exit codes:
    0  report written, nothing rejected
    1  report written, but some records or files were rejected
    2  no report: invalid settings, or no export files
"""

import argparse
import sys
from datetime import datetime

from pydantic import ValidationError
from pydantic_settings import SettingsError

from incident_api.loading import load_exports
from incident_api.report import build_report, write_report
from incident_api.settings import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="incident-report")
    parser.add_argument(
        "--summary-only", action="store_true", help="leave the rejected list out of the report"
    )
    args = parser.parse_args(argv)

    try:
        settings = Settings()
    except SettingsError as error:  # a variable that couldn't even be parsed, e.g. invalid JSON
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2
    except ValidationError as error:
        print("error: invalid settings", file=sys.stderr)
        for issue in error.errors(include_url=False):
            field = ".".join(str(part) for part in issue["loc"]) or "settings"
            print(f"  {field}: {issue['msg']}", file=sys.stderr)
        return 2

    paths = sorted(settings.input_dir.glob("*.json"))
    if not paths:
        print(f"error: no .json export files in {settings.input_dir}", file=sys.stderr)
        return 2

    tickets, rejections = load_exports(paths)
    report = build_report(
        tickets, rejections, sla_hours=settings.sla_hours, generated_at=datetime.now().astimezone()
    )
    write_report(report, settings.output_file, include_rejected=not args.summary_only)

    totals = report.totals
    print(
        f"Read {len(paths)} export files: {totals.valid_records} valid records, "
        f"{totals.unique_tickets} unique tickets, {totals.rejected} rejected"
    )
    for rejection in rejections:
        problems = "; ".join(rejection.problems)
        if rejection.record is None:  # a whole file; its message starts with the file name
            print(f"  rejected file {problems}", file=sys.stderr)
        else:
            print(f"  rejected {rejection.file}[{rejection.record}]: {problems}", file=sys.stderr)
    print(f"Report written to {settings.output_file}")
    return 1 if rejections else 0
