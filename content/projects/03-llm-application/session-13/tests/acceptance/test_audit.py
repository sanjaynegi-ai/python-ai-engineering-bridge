"""Acceptance tests for the routing audit log (Session 13 workbook). Do not edit.

These tests define "done" for the AI-assisted feature: give them to your assistant as
the check it must pass, and review its code as you would a colleague's.
"""

import json
import shutil
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from incident_triage.audit import AuditRecord, append_audit, audit_records
from incident_triage.cli import main
from incident_triage.errors import LLMInvalidOutput, LLMRefusal, LLMUnavailable
from incident_triage.models import IncidentReport, Triage, TriageResult, Usage
from incident_triage.routing import PlainRouter, RoutingRun, route_all

SAMPLE = Path(__file__).parents[2] / "data" / "reports.jsonl"
NOON = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
FIELDS = {
    "timestamp",
    "report_id",
    "action",
    "team",
    "reasons",
    "path",
    "attempts",
    "model",
    "llm_error",
    "input_tokens",
    "output_tokens",
}

# Text that must never reach the audit log
SECRET_REPORT = "Customer Jane Example, card ending 4242, can't check out"
SECRET_SUMMARY = "Checkout fails for Jane Example"
SECRET_ERROR = "model echoed: Jane Example 4242"


def make_triage(model: str = "gpt-5.6-terra", **changes) -> Triage:
    fields = {
        "priority": "P2",
        "team": "platform",
        "category": "degradation",
        "affected_system": "checkout API",
        "summary": SECRET_SUMMARY,
        "tags": ["checkout"],
    }
    return Triage(
        result=TriageResult(**(fields | changes)),
        model=model,
        usage=Usage(input_tokens=400, output_tokens=60),
    )


class ScriptedTriager:
    """Plays its script in order; the last step repeats."""

    def __init__(self, *steps):
        self.steps = list(steps)
        self.calls = 0

    def triage(self, report):
        step = self.steps[min(self.calls, len(self.steps) - 1)]
        self.calls += 1
        if isinstance(step, Exception):
            raise step
        return step


def run_of(*steps, fallback_priority: str = "P3") -> RoutingRun:
    """One routing per step: each report gets the next scripted outcome."""
    fallback = ScriptedTriager(make_triage(model="keyword-rules", priority=fallback_priority))
    routings = []
    for number, step in enumerate(steps, 1):
        steps_for_report = step if isinstance(step, tuple) else (step,)
        router = PlainRouter(ScriptedTriager(*steps_for_report), fallback)
        report = IncidentReport(id=f"RPT-{number}", text=SECRET_REPORT)
        routings.extend(route_all(router, [report]).routings)
    return RoutingRun(routings=routings)


# --- audit_records ----------------------------------------------------------------------


def test_one_record_per_routing_in_order():
    run = run_of(make_triage(priority="P1"), make_triage(), LLMRefusal("no"))

    records = audit_records(run, at=NOON)

    assert all(isinstance(record, AuditRecord) for record in records)
    assert [r.report_id for r in records] == ["RPT-1", "RPT-2", "RPT-3"]
    assert [r.action for r in records] == ["page", "queue", "review"]


def test_a_successful_triage():
    (record,) = audit_records(run_of(make_triage(priority="P1")), at=NOON)

    assert record.timestamp == NOON
    assert record.team == "platform"
    assert record.reasons == []
    assert record.path == ["triage", "check", "page"]
    assert record.attempts == 1
    assert record.model == "gpt-5.6-terra"
    assert record.llm_error is False
    assert (record.input_tokens, record.output_tokens) == (400, 60)


def test_a_refusal():
    (record,) = audit_records(run_of(LLMRefusal("I can't help")), at=NOON)

    assert record.action == "review"
    assert record.team is None
    assert record.reasons == ["the model refused"]  # without the model's own words
    assert record.model is None
    assert record.llm_error is True
    assert (record.input_tokens, record.output_tokens) == (0, 0)


def test_a_review_has_no_team_even_when_the_triage_named_one():
    (record,) = audit_records(run_of(make_triage(priority="P1", affected_system=None)), at=NOON)

    assert record.action == "review"
    assert record.team is None  # where it was dispatched, not the triage's opinion
    assert record.reasons == ["P1 without an affected system"]


def test_a_fallback_after_an_outage():
    (record,) = audit_records(run_of(LLMUnavailable("timed out")), at=NOON)

    assert record.model == "keyword-rules"
    assert record.llm_error is True
    assert record.path == ["triage", "fallback", "check", "queue"]


def test_a_retry_that_succeeded_still_counts_as_an_llm_error():
    (record,) = audit_records(run_of((LLMInvalidOutput("bad"), make_triage())), at=NOON)

    assert record.attempts == 2
    assert record.llm_error is True
    assert record.model == "gpt-5.6-terra"


def test_the_time_is_stored_in_utc():
    zurich_summer = timezone(timedelta(hours=2))

    (record,) = audit_records(
        run_of(make_triage()), at=datetime(2026, 10, 23, 14, 0, tzinfo=zurich_summer)
    )

    assert record.timestamp == NOON
    assert record.timestamp.utcoffset() == timedelta(0)


def test_a_naive_time_is_rejected():
    with pytest.raises(ValueError):
        audit_records(run_of(make_triage()), at=datetime(2026, 10, 23, 12, 0))


def test_an_empty_run_has_no_records():
    assert audit_records(RoutingRun(routings=[]), at=NOON) == []


# --- append_audit -------------------------------------------------------------------------


def read_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_records_are_written_as_json_lines(tmp_path):
    path = tmp_path / "logs" / "audit.jsonl"  # the folder doesn't exist yet
    records = audit_records(run_of(make_triage(priority="P1"), LLMRefusal("no")), at=NOON)

    written = append_audit(path, records)

    lines = read_lines(path)
    assert written == 2
    assert [line["report_id"] for line in lines] == ["RPT-1", "RPT-2"]
    assert all(set(line) == FIELDS for line in lines)
    assert datetime.fromisoformat(lines[0]["timestamp"]) == NOON


def test_appending_keeps_earlier_lines(tmp_path):
    path = tmp_path / "audit.jsonl"
    append_audit(path, audit_records(run_of(make_triage()), at=NOON))
    first = path.read_text(encoding="utf-8")

    append_audit(path, audit_records(run_of(make_triage(), make_triage()), at=NOON))

    text = path.read_text(encoding="utf-8")
    assert text.startswith(first)
    assert len(read_lines(path)) == 3


def test_nothing_private_is_written(tmp_path):
    path = tmp_path / "audit.jsonl"
    run = run_of(
        make_triage(priority="P1"),
        LLMRefusal(SECRET_ERROR),
        (LLMInvalidOutput(SECRET_ERROR), make_triage()),
        LLMUnavailable(SECRET_ERROR),
    )

    append_audit(path, audit_records(run, at=NOON))

    text = path.read_text(encoding="utf-8")
    for secret in ("Jane Example", "4242", SECRET_SUMMARY):
        assert secret not in text


# --- The command line ----------------------------------------------------------------------


@pytest.fixture
def reports_file(clean_env, tmp_path) -> Path:
    target = tmp_path / "reports.jsonl"
    shutil.copy(SAMPLE, target)
    return target


def test_cli_appends_one_record_per_report(reports_file, tmp_path, capsys):
    audit = tmp_path / "audit.jsonl"
    args = [str(reports_file), "--offline", "--route", "graph", "--out", str(tmp_path / "r.json")]

    assert main([*args, "--audit", str(audit)]) == 0
    assert main([*args, "--audit", str(audit)]) == 0

    lines = read_lines(audit)
    assert len(lines) == 24
    assert lines[0]["report_id"] == lines[12]["report_id"] == "RPT-1001"
    assert "Audit: 12 records appended" in capsys.readouterr().out


def test_cli_audit_times_are_now_in_utc(reports_file, tmp_path):
    audit = tmp_path / "audit.jsonl"
    before = datetime.now(UTC)

    main([str(reports_file), "--offline", "--route", "plain", "--audit", str(audit)])

    stamp = datetime.fromisoformat(read_lines(audit)[0]["timestamp"])
    assert stamp.utcoffset() == timedelta(0)
    assert before - timedelta(seconds=1) <= stamp <= datetime.now(UTC) + timedelta(seconds=1)


def test_cli_audit_contains_no_report_text(reports_file, tmp_path):
    audit = tmp_path / "audit.jsonl"

    main([str(reports_file), "--offline", "--route", "graph", "--audit", str(audit)])

    text = audit.read_text(encoding="utf-8")
    for line in SAMPLE.read_text(encoding="utf-8").splitlines():
        report_text = json.loads(line)["text"]
        assert report_text[:30] not in text


def test_cli_audit_needs_route(reports_file, tmp_path, capsys):
    code = main([str(reports_file), "--offline", "--audit", str(tmp_path / "audit.jsonl")])

    assert code == 2
    assert "--audit requires --route" in capsys.readouterr().err
    assert not (tmp_path / "audit.jsonl").exists()


def test_cli_unwritable_audit_log(reports_file, tmp_path, capsys):
    blocked = tmp_path / "audit-is-a-folder"
    blocked.mkdir()
    out = tmp_path / "r.json"

    args = [str(reports_file), "--offline", "--route", "graph", "--out", str(out)]

    code = main([*args, "--audit", str(blocked)])

    captured = capsys.readouterr()
    assert code == 2
    assert "audit" in captured.err
    assert "Traceback" not in captured.err
    assert out.exists()  # the routing results are still written
