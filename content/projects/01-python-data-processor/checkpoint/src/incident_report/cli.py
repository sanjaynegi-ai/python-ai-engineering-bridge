"""Command-line entry point: `incident-report [CONFIG_PATH]`.

Exit codes:
    0  report written, nothing rejected
    1  report written, but some records or files were rejected
    2  no report: bad configuration, or no export files
"""

import sys
from datetime import datetime
from pathlib import Path

from incident_report.errors import ConfigError
from incident_report.loading import load_config, load_exports
from incident_report.report import build_report, write_report


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    config_path = Path(args[0]) if args else Path("config.json")

    try:
        config = load_config(config_path)
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    paths = sorted(config.input_dir.glob("*.json"))
    if not paths:
        print(f"error: no .json export files in {config.input_dir}", file=sys.stderr)
        return 2

    tickets, rejections = load_exports(paths, sla_hours=config.sla_hours)
    report = build_report(
        tickets, rejections, sla_hours=config.sla_hours, generated_at=datetime.now().astimezone()
    )
    write_report(report, config.output_file)

    totals = report["totals"]
    print(
        f"Read {len(paths)} export files: {totals['valid_records']} valid records, "
        f"{totals['unique_tickets']} unique tickets, {totals['rejected']} rejected"
    )
    for rejection in rejections:
        problems = "; ".join(rejection.problems)
        if rejection.record is None:  # a whole file; its message starts with the file name
            print(f"  rejected file {problems}", file=sys.stderr)
        else:
            print(f"  rejected {rejection.file}[{rejection.record}]: {problems}", file=sys.stderr)
    print(f"Report written to {config.output_file}")
    return 1 if rejections else 0
