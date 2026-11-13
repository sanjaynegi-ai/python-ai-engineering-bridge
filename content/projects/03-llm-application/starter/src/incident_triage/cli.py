"""Command-line entry point: `incident-triage REPORTS.jsonl [--offline] [--out FILE]`.

Exit codes:
    0  every report was triaged
    1  some reports could not be triaged (listed on stderr)
    2  no run: invalid settings, a missing or invalid reports file, or the
       provider rejected the configuration (key or model)
"""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import SettingsError

from incident_triage.errors import LLMConfigurationError, ReportFileError
from incident_triage.llm import OpenAITriager, Triager
from incident_triage.loading import load_reports
from incident_triage.offline import KeywordTriager
from incident_triage.service import triage_all
from incident_triage.settings import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="incident-triage")
    parser.add_argument("reports", type=Path, help="a JSON Lines file of incident reports")
    parser.add_argument("--out", type=Path, default=Path("out/triage.json"))
    parser.add_argument(
        "--offline",
        action="store_true",
        help="use keyword rules instead of the LLM (no key, no cost)",
    )
    args = parser.parse_args(argv)

    try:
        settings = Settings()
    except (SettingsError, ValidationError) as error:
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2

    try:
        reports = load_reports(args.reports)
        triager: Triager = (
            KeywordTriager() if args.offline else OpenAITriager.from_settings(settings)
        )
        run = triage_all(
            triager,
            reports,
            input_usd_per_million=settings.llm_input_usd_per_million,
            output_usd_per_million=settings.llm_output_usd_per_million,
        )
    except (ReportFileError, LLMConfigurationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for outcome in run.outcomes:
        if outcome.triage is None:
            print(f"{outcome.report_id}  FAILED  {outcome.error}", file=sys.stderr)
            continue
        result = outcome.triage.result
        print(f"{outcome.report_id}  {result.priority}  {result.team:<10}  {result.summary}")
    cost = (
        "unknown (set the LLM_*_USD_PER_MILLION prices)"
        if run.cost_usd is None
        else f"${run.cost_usd:.4f}"
    )
    print(
        f"{len(run.outcomes) - len(run.failed)} of {len(run.outcomes)} triaged; "
        f"{run.input_tokens} input and {run.output_tokens} output tokens; cost {cost}"
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Written to {args.out}")
    return 1 if run.failed else 0
