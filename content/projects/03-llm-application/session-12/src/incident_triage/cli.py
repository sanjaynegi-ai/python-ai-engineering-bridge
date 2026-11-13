"""Command-line entry point:
`incident-triage REPORTS.jsonl [--engine ENGINE] [--route WORKFLOW] [--out FILE]`.

Engines:
    direct     the OpenAI SDK, called directly (Session 09); the default
    langchain  the same triage through LangChain (Session 10)
    offline    keyword rules: no key, no network, no cost (also: --offline)

Workflows (Session 12), which also decide where each report goes:
    plain      the routing workflow in plain Python
    graph      the same workflow as a LangGraph graph

Exit codes:
    0  every report was triaged (or, with --route, routed; review is a route)
    1  some reports could not be triaged (listed on stderr); not used with --route
    2  no run: invalid settings, a missing or invalid reports file, or the
       provider rejected the configuration (key or model)
"""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import SettingsError

from incident_triage.errors import LLMConfigurationError, ReportFileError
from incident_triage.langchain_triager import LangChainTriager
from incident_triage.llm import OpenAITriager, Triager
from incident_triage.loading import load_reports
from incident_triage.offline import KeywordTriager
from incident_triage.routing import PlainRouter, Router, RoutingRun, route_all
from incident_triage.service import triage_all
from incident_triage.settings import Settings
from incident_triage.workflow import GraphRouter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="incident-triage")
    parser.add_argument("reports", type=Path, help="a JSON Lines file of incident reports")
    parser.add_argument("--out", type=Path, default=Path("out/triage.json"))
    parser.add_argument("--engine", choices=["direct", "langchain", "offline"], default="direct")
    parser.add_argument(
        "--offline",
        action="store_const",
        dest="engine",
        const="offline",
        help="the same as --engine offline: keyword rules, no key, no cost",
    )
    parser.add_argument(
        "--route",
        choices=["plain", "graph"],
        help="also decide where each report goes: page, queue or review",
    )
    args = parser.parse_args(argv)

    try:
        settings = Settings()
    except (SettingsError, ValidationError) as error:
        print(f"error: invalid settings: {error}", file=sys.stderr)
        return 2

    try:
        reports = load_reports(args.reports)
        triager: Triager
        if args.engine == "offline":
            triager = KeywordTriager()
        elif args.engine == "langchain":
            triager = LangChainTriager.from_settings(settings)
        else:
            triager = OpenAITriager.from_settings(settings)
        if args.route is not None:
            router: Router
            if args.route == "graph":
                router = GraphRouter(triager, KeywordTriager())
            else:
                router = PlainRouter(triager, KeywordTriager())
            routing_run = route_all(router, reports)
            return print_routing(routing_run, args.out)
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


def print_routing(run: RoutingRun, out: Path) -> int:
    for routing in run.routings:
        dispatch = routing.dispatch
        if dispatch.action == "review":
            detail = "; ".join(dispatch.reasons)
        else:
            detail = f"{dispatch.team:<10}  {routing.triage.result.summary}"
        print(f"{routing.report_id}  {dispatch.action:<6}  {detail}")
    print(
        f"{run.count('page')} paged, {run.count('queue')} queued, {run.count('review')} for review"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Written to {out}")
    return 0
