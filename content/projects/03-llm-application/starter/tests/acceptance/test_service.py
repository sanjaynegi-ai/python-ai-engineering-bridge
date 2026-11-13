"""Acceptance tests for triage_all (workbook Milestone 4). Do not edit.

These tests use a scripted triager, not the OpenAI SDK: the service only depends
on the Triager protocol, so any object with a `triage(report)` method will do.
"""

import pytest

from incident_triage.errors import (
    LLMConfigurationError,
    LLMInvalidOutput,
    LLMRefusal,
    LLMUnavailable,
)
from incident_triage.models import Triage, TriageResult, TriageRun, Usage
from incident_triage.service import triage_all

RESULT = TriageResult(
    priority="P3",
    team="it-support",
    category="hardware",
    affected_system=None,
    summary="A keyboard key is missing.",
    tags=["laptop"],
)


class ScriptedTriager:
    """Returns a triage, or raises the exception scripted for that report id."""

    def __init__(self, failures: dict[str, Exception] | None = None) -> None:
        self.failures = failures or {}
        self.seen: list[str] = []

    def triage(self, report):
        self.seen.append(report.id)
        if report.id in self.failures:
            raise self.failures[report.id]
        return Triage(
            result=RESULT, model="scripted", usage=Usage(input_tokens=1000, output_tokens=100)
        )


@pytest.fixture
def reports(make_report):
    return [make_report(f"RPT-{n}", f"report {n}") for n in (1, 2, 3, 4)]


def test_every_report_gets_an_outcome_in_order(reports):
    run = triage_all(ScriptedTriager(), reports)

    assert isinstance(run, TriageRun)
    assert [outcome.report_id for outcome in run.outcomes] == ["RPT-1", "RPT-2", "RPT-3", "RPT-4"]
    assert all(outcome.triage.result == RESULT for outcome in run.outcomes)
    assert run.failed == []


def test_one_report_failing_does_not_stop_the_run(reports):
    triager = ScriptedTriager(
        {
            "RPT-2": LLMRefusal("the model declined: no"),
            "RPT-3": LLMUnavailable("RateLimitError after retries"),
            "RPT-4": LLMInvalidOutput("invalid triage from the model: summary: too long"),
        }
    )

    run = triage_all(triager, reports)

    assert triager.seen == ["RPT-1", "RPT-2", "RPT-3", "RPT-4"]
    assert run.outcomes[0].triage is not None
    assert [outcome.report_id for outcome in run.failed] == ["RPT-2", "RPT-3", "RPT-4"]
    assert run.outcomes[1].error == "the model declined: no"
    assert run.outcomes[1].triage is None


def test_a_configuration_problem_stops_the_run(reports):
    triager = ScriptedTriager(
        {"RPT-2": LLMConfigurationError("the provider rejected the API key (401)")}
    )

    with pytest.raises(LLMConfigurationError):
        triage_all(triager, reports)

    assert triager.seen == ["RPT-1", "RPT-2"]  # no point sending RPT-3 and RPT-4


def test_unexpected_exceptions_are_not_swallowed(reports):
    with pytest.raises(KeyError):
        triage_all(ScriptedTriager({"RPT-2": KeyError("a bug")}), reports)


def test_token_totals_count_successful_reports(reports):
    run = triage_all(ScriptedTriager({"RPT-4": LLMRefusal("no")}), reports)

    assert (run.input_tokens, run.output_tokens) == (3000, 300)


def test_cost_with_prices(reports):
    run = triage_all(
        ScriptedTriager(), reports, input_usd_per_million=0.10, output_usd_per_million=0.50
    )

    assert run.cost_usd == pytest.approx((4000 * 0.10 + 400 * 0.50) / 1_000_000)


def test_cost_is_unknown_without_prices(reports):
    assert triage_all(ScriptedTriager(), reports).cost_usd is None
    assert triage_all(ScriptedTriager(), reports, input_usd_per_million=0.1).cost_usd is None


def test_no_reports():
    run = triage_all(ScriptedTriager(), [])

    assert (run.outcomes, run.input_tokens, run.cost_usd) == ([], 0, None)
