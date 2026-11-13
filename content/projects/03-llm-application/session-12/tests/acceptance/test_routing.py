"""Acceptance tests for the routing workflow (Session 12 workbook). Do not edit.

Most tests are a contract: they run twice, once against PlainRouter and once against
GraphRouter, with the same scripted triagers and the same expectations. Neither the
OpenAI SDK nor the network is involved: routers depend only on the Triager protocol.
"""

import json
import shutil
from pathlib import Path

import pytest
from langgraph.errors import GraphRecursionError

from incident_triage.cli import main
from incident_triage.errors import (
    LLMConfigurationError,
    LLMInvalidOutput,
    LLMRefusal,
    LLMUnavailable,
)
from incident_triage.models import IncidentReport, Triage, TriageResult, Usage
from incident_triage.offline import KeywordTriager
from incident_triage.routing import (
    Dispatch,
    PlainRouter,
    Routing,
    RoutingRun,
    review_reasons,
    route_all,
)
from incident_triage.workflow import GraphRouter, build_workflow

REPORT = IncidentReport(id="RPT-1", text="Checkout API returns 502 for all customers.")
SAMPLE = Path(__file__).parents[2] / "data" / "reports.jsonl"


def make_triage(model: str = "gpt-5.6-terra", **changes) -> Triage:
    fields = {
        "priority": "P2",
        "team": "platform",
        "category": "degradation",
        "affected_system": "checkout API",
        "summary": "Checkout API is slow.",
        "tags": ["checkout"],
    }
    result = TriageResult(**(fields | changes))
    return Triage(result=result, model=model, usage=Usage(input_tokens=400, output_tokens=60))


class ScriptedTriager:
    """Plays its script in order: each step is a Triage to return or an exception to raise.
    The last step repeats once the script runs out."""

    def __init__(self, *steps: Triage | Exception) -> None:
        self.steps = list(steps)
        self.calls = 0

    def triage(self, report: IncidentReport) -> Triage:
        step = self.steps[min(self.calls, len(self.steps) - 1)]
        self.calls += 1
        if isinstance(step, Exception):
            raise step
        return step


ROUTERS = {"plain": PlainRouter, "graph": GraphRouter}


@pytest.fixture(params=list(ROUTERS))
def make_router(request):
    """A function that builds the router under test from a primary and a fallback triager."""
    return ROUTERS[request.param]


@pytest.fixture
def fallback() -> ScriptedTriager:
    return ScriptedTriager(make_triage(model="keyword-rules", priority="P3"))


# --- The business rules -----------------------------------------------------------


def test_a_good_triage_breaks_no_rules():
    assert review_reasons(make_triage()) == []


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"team": "unknown"}, "no owning team"),
        ({"priority": "P1", "affected_system": None}, "P1 without an affected system"),
        ({"category": "security", "priority": "P3"}, "security incident below P2"),
        ({"category": "security", "priority": "P4"}, "security incident below P2"),
    ],
)
def test_each_rule(changes, reason):
    assert review_reasons(make_triage(**changes)) == [reason]


def test_security_rule_allows_p2_and_above():
    assert review_reasons(make_triage(category="security", priority="P2")) == []


def test_keyword_rules_are_not_trusted_with_high_priorities():
    assert review_reasons(make_triage(model="keyword-rules", priority="P1")) == [
        "high priority from keyword rules"
    ]
    assert review_reasons(make_triage(model="keyword-rules", priority="P2")) == [
        "high priority from keyword rules"
    ]
    assert review_reasons(make_triage(model="keyword-rules", priority="P3")) == []


def test_every_broken_rule_is_listed_in_order():
    triage = make_triage(model="keyword-rules", priority="P1", team="unknown", affected_system=None)

    assert review_reasons(triage) == [
        "no owning team",
        "P1 without an affected system",
        "high priority from keyword rules",
    ]


# --- The contract: both routers -------------------------------------------------------


def test_p1_with_a_team_and_a_system_pages_the_team(make_router, fallback):
    triager = ScriptedTriager(make_triage(priority="P1", category="outage"))

    routing = make_router(triager, fallback).route(REPORT)

    assert isinstance(routing, Routing)
    assert routing.dispatch == Dispatch(action="page", team="platform", reasons=[])
    assert routing.path == ["triage", "check", "page"]
    assert routing.attempts == 1
    assert routing.error is None
    assert routing.report_id == "RPT-1"
    assert routing.triage.result.priority == "P1"
    assert fallback.calls == 0


@pytest.mark.parametrize("priority", ["P2", "P3", "P4"])
def test_lower_priorities_are_queued_for_the_team(make_router, fallback, priority):
    triager = ScriptedTriager(make_triage(priority=priority, team="network"))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.dispatch == Dispatch(action="queue", team="network", reasons=[])
    assert routing.path == ["triage", "check", "queue"]


def test_a_broken_rule_sends_it_to_review(make_router, fallback):
    triager = ScriptedTriager(make_triage(team="unknown"))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.dispatch == Dispatch(action="review", team=None, reasons=["no owning team"])
    assert routing.path == ["triage", "check", "review"]
    assert routing.triage is not None


def test_a_refusal_goes_to_review_without_a_fallback(make_router, fallback):
    triager = ScriptedTriager(LLMRefusal("I can't help with that."))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.path == ["triage", "review"]
    assert routing.triage is None
    assert routing.error == "I can't help with that."
    assert routing.dispatch == Dispatch(
        action="review", team=None, reasons=["the model refused: I can't help with that."]
    )
    assert (triager.calls, fallback.calls) == (1, 0)


def test_invalid_output_is_retried(make_router, fallback):
    triager = ScriptedTriager(LLMInvalidOutput("summary is empty"), make_triage())

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.path == ["triage", "triage", "check", "queue"]
    assert routing.attempts == 2
    assert routing.triage.model == "gpt-5.6-terra"
    assert routing.error == "summary is empty"  # the last error is kept, even after a success
    assert fallback.calls == 0


def test_invalid_output_every_time_uses_the_fallback(make_router, fallback):
    triager = ScriptedTriager(LLMInvalidOutput("truncated JSON"))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.path == ["triage", "triage", "fallback", "check", "queue"]
    assert (routing.attempts, triager.calls, fallback.calls) == (2, 2, 1)
    assert routing.triage.model == "keyword-rules"
    assert routing.error == "truncated JSON"


def test_an_unavailable_provider_is_not_retried_again(make_router, fallback):
    # The SDK has already retried; one more attempt here would only add delay.
    triager = ScriptedTriager(LLMUnavailable("timed out"))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.path == ["triage", "fallback", "check", "queue"]
    assert (routing.attempts, triager.calls, fallback.calls) == (1, 1, 1)
    assert routing.error == "timed out"


def test_a_high_priority_fallback_goes_to_review(make_router):
    triager = ScriptedTriager(LLMUnavailable("timed out"))
    fallback = ScriptedTriager(make_triage(model="keyword-rules", priority="P1"))

    routing = make_router(triager, fallback).route(REPORT)

    assert routing.path == ["triage", "fallback", "check", "review"]
    assert routing.dispatch.reasons == ["high priority from keyword rules"]


def test_a_configuration_error_stops_everything(make_router, fallback):
    triager = ScriptedTriager(LLMConfigurationError("the key was rejected"))

    with pytest.raises(LLMConfigurationError):
        make_router(triager, fallback).route(REPORT)

    assert fallback.calls == 0


@pytest.mark.parametrize("max_attempts", [1, 3])
def test_max_attempts(make_router, fallback, max_attempts):
    triager = ScriptedTriager(LLMInvalidOutput("bad"))

    routing = make_router(triager, fallback, max_attempts=max_attempts).route(REPORT)

    assert triager.calls == routing.attempts == max_attempts
    assert routing.path == ["triage"] * max_attempts + ["fallback", "check", "queue"]


def test_max_attempts_must_be_positive(make_router, fallback):
    with pytest.raises(ValueError):
        make_router(ScriptedTriager(make_triage()), fallback, max_attempts=0)


def test_the_router_can_be_reused(make_router, fallback):
    triager = ScriptedTriager(LLMInvalidOutput("bad"), make_triage(), make_triage(priority="P1"))
    router = make_router(triager, fallback)

    first = router.route(REPORT)
    second = router.route(REPORT)

    assert first.path == ["triage", "triage", "check", "queue"]
    assert second.path == ["triage", "check", "page"]  # nothing left over from the first
    assert second.attempts == 1
    assert second.error is None


def test_route_all_keeps_the_order(make_router, fallback):
    reports = [IncidentReport(id=f"RPT-{n}", text="x") for n in range(3)]
    triager = ScriptedTriager(make_triage(priority="P1"), make_triage(), LLMRefusal("no"))

    run = route_all(make_router(triager, fallback), reports)

    assert isinstance(run, RoutingRun)
    assert [r.report_id for r in run.routings] == ["RPT-0", "RPT-1", "RPT-2"]
    assert [r.dispatch.action for r in run.routings] == ["page", "queue", "review"]
    assert (run.count("page"), run.count("queue"), run.count("review")) == (1, 1, 1)


def test_a_routing_run_is_json(make_router, fallback):
    triager = ScriptedTriager(make_triage())

    run = route_all(make_router(triager, fallback), [REPORT])

    data = json.loads(run.model_dump_json())
    assert data["routings"][0]["dispatch"]["action"] == "queue"
    assert data["routings"][0]["path"] == ["triage", "check", "queue"]


# --- The graph itself -----------------------------------------------------------------


def edges(graph) -> set[tuple[str, str]]:
    return {(edge.source, edge.target) for edge in graph.get_graph().edges}


def test_the_graph_has_the_six_nodes():
    graph = build_workflow(ScriptedTriager(make_triage()), KeywordTriager())

    nodes = set(graph.get_graph().nodes) - {"__start__", "__end__"}

    assert nodes == {"triage", "fallback", "check", "page", "queue", "review"}


def test_the_graph_declares_every_route():
    # Without declared destinations, LangGraph can't draw or check the routes.
    graph = build_workflow(ScriptedTriager(make_triage()), KeywordTriager())

    assert edges(graph) == {
        ("__start__", "triage"),
        ("triage", "triage"),
        ("triage", "fallback"),
        ("triage", "check"),
        ("triage", "review"),
        ("fallback", "check"),
        ("check", "page"),
        ("check", "queue"),
        ("check", "review"),
        ("page", "__end__"),
        ("queue", "__end__"),
        ("review", "__end__"),
    }


def test_streaming_shows_each_step_and_what_it_changed():
    triager = ScriptedTriager(LLMInvalidOutput("bad"), make_triage(priority="P1"))
    graph = build_workflow(triager, KeywordTriager())

    updates = list(
        graph.stream({"report": REPORT, "attempts": 0, "path": []}, stream_mode="updates")
    )

    assert [next(iter(update)) for update in updates] == ["triage", "triage", "check", "page"]
    first = updates[0]["triage"]
    assert first["attempts"] == 1
    assert "dispatch" not in first  # a node returns only what it changes


def test_the_graph_router_limits_the_steps():
    router = GraphRouter(ScriptedTriager(make_triage()), KeywordTriager(), max_attempts=2)
    looping = build_workflow(
        ScriptedTriager(LLMInvalidOutput("bad")), KeywordTriager(), max_attempts=50
    )

    with pytest.raises(GraphRecursionError):
        looping.invoke(
            {"report": REPORT, "attempts": 0, "path": []},
            {"recursion_limit": router.recursion_limit},
        )
    assert router.recursion_limit < 10


def test_the_graph_router_passes_its_limit_to_the_graph():
    router = GraphRouter(ScriptedTriager(LLMInvalidOutput("bad")), KeywordTriager())
    router.recursion_limit = 2  # too small for any complete path

    with pytest.raises(GraphRecursionError):
        router.route(REPORT)


# --- The command line -------------------------------------------------------------------


@pytest.fixture
def reports_file(clean_env, tmp_path) -> Path:
    target = tmp_path / "reports.jsonl"
    shutil.copy(SAMPLE, target)
    return target


@pytest.mark.parametrize("workflow", ["plain", "graph"])
def test_cli_routes_every_sample_report_offline(reports_file, tmp_path, capsys, workflow):
    out = tmp_path / f"{workflow}.json"

    code = main([str(reports_file), "--offline", "--route", workflow, "--out", str(out)])

    assert code == 0
    run = json.loads(out.read_text(encoding="utf-8"))
    assert len(run["routings"]) == 12
    assert {r["dispatch"]["action"] for r in run["routings"]} <= {"page", "queue", "review"}
    assert "for review" in capsys.readouterr().out


def test_cli_both_workflows_agree(reports_file, tmp_path):
    main([str(reports_file), "--offline", "--route", "plain", "--out", str(tmp_path / "p.json")])
    main([str(reports_file), "--offline", "--route", "graph", "--out", str(tmp_path / "g.json")])

    assert (tmp_path / "p.json").read_text(encoding="utf-8") == (tmp_path / "g.json").read_text(
        encoding="utf-8"
    )


def test_cli_graph_workflow_runs_the_graph(reports_file, tmp_path, monkeypatch):
    calls = []
    original = GraphRouter.route

    def spy(self, report):
        calls.append(report.id)
        return original(self, report)

    monkeypatch.setattr(GraphRouter, "route", spy)

    main([str(reports_file), "--offline", "--route", "graph", "--out", str(tmp_path / "g.json")])

    assert len(calls) == 12


def test_cli_route_without_a_key(reports_file, capsys):
    code = main([str(reports_file), "--route", "graph"])

    assert code == 2
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().err
