"""Acceptance tests for incident_report.loading. Do not edit."""

import json

import pytest

from incident_report.errors import ConfigError, ExportError
from incident_report.loading import load_config, load_exports, read_export, validate_record
from incident_report.models import Config, Rejection, Ticket

CONFIG = {
    "input_dir": "data/exports",
    "output_file": "out/report.json",
    "sla_hours": {"P1": 4, "P2": 24, "P3": 72, "P4": 168},
}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------- load_config
def test_load_config_resolves_paths_relative_to_the_file(tmp_path):
    path = write_json(tmp_path / "settings" / "config.json", CONFIG)

    config = load_config(path)

    assert config == Config(
        input_dir=tmp_path / "settings" / "data" / "exports",
        output_file=tmp_path / "settings" / "out" / "report.json",
        sla_hours=CONFIG["sla_hours"],
    )


def test_load_config_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="missing.json") as caught:
        load_config(tmp_path / "missing.json")

    assert isinstance(caught.value.__cause__, FileNotFoundError)


def test_load_config_malformed_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text('{"input_dir": "data",\n "sla_hours": }', encoding="utf-8")

    with pytest.raises(ConfigError, match="broken.json") as caught:
        load_config(path)

    assert isinstance(caught.value.__cause__, json.JSONDecodeError)


def test_load_config_missing_key(tmp_path):
    config = {key: value for key, value in CONFIG.items() if key != "sla_hours"}
    path = write_json(tmp_path / "config.json", config)

    with pytest.raises(ConfigError, match="sla_hours"):
        load_config(path)


@pytest.mark.parametrize(
    "data",
    [
        [CONFIG],
        CONFIG | {"output_file": 7},
        CONFIG | {"sla_hours": {"P1": "4"}},
        CONFIG | {"sla_hours": {"P1": 0}},
        CONFIG | {"sla_hours": {"P1": True}},
        CONFIG | {"sla_hours": [4, 24]},
    ],
    ids=["list", "path-number", "hours-string", "hours-zero", "hours-true", "hours-list"],
)
def test_load_config_rejects_bad_values(tmp_path, data):
    path = write_json(tmp_path / "config.json", data)

    with pytest.raises(ConfigError):
        load_config(path)


# ---------------------------------------------------------------- read_export
def test_read_export_reads_utf8(tmp_path, make_record):
    path = write_json(tmp_path / "tickets.json", [make_record()])

    assert read_export(path)[0]["title"] == "Badge readers offline at the Zürich depot"


def test_read_export_missing_file(tmp_path):
    with pytest.raises(ExportError, match="tickets-gone.json") as caught:
        read_export(tmp_path / "tickets-gone.json")

    assert isinstance(caught.value.__cause__, FileNotFoundError)


def test_read_export_malformed_json_names_the_line(tmp_path):
    path = tmp_path / "tickets-cut.json"
    path.write_text('[\n  {"id": "INC-1"},\n  {"id": "INC-2",\n', encoding="utf-8")

    with pytest.raises(ExportError, match=r"tickets-cut\.json.*line 4") as caught:
        read_export(path)

    assert isinstance(caught.value.__cause__, json.JSONDecodeError)


def test_read_export_not_utf8(tmp_path):
    path = tmp_path / "tickets-latin1.json"
    path.write_bytes('[{"title": "Zürich"}]'.encode("latin-1"))

    with pytest.raises(ExportError, match="tickets-latin1.json") as caught:
        read_export(path)

    assert isinstance(caught.value.__cause__, UnicodeDecodeError)


def test_read_export_not_a_list(tmp_path):
    path = write_json(tmp_path / "tickets-object.json", {"tickets": []})

    with pytest.raises(ExportError, match="tickets-object.json"):
        read_export(path)


# ---------------------------------------------------------------- validate_record
def test_validate_valid_record(make_record, sla_hours):
    assert validate_record(make_record(), sla_hours=sla_hours) == []
    assert validate_record(make_record(assignee="li"), sla_hours=sla_hours) == []


def test_validate_not_an_object(sla_hours):
    assert validate_record(["INC-1"], sla_hours=sla_hours) == ["record is not a JSON object"]


def test_validate_types(make_record, sla_hours):
    record = make_record(age_hours="12", assignee=7)
    del record["id"]

    assert validate_record(record, sla_hours=sla_hours) == [
        "missing field 'id'",
        "field 'age_hours' must be int, got str",
        "field 'assignee' must be str or None, got int",
    ]


def test_validate_rejects_bool_as_int(make_record, sla_hours):
    problems = validate_record(make_record(age_hours=True), sla_hours=sla_hours)

    assert problems == ["field 'age_hours' must be int, got bool"]


def test_validate_values(make_record, sla_hours):
    record = make_record(age_hours=-3, priority="P9", tags=["dns", 4])

    assert validate_record(record, sla_hours=sla_hours) == [
        "field 'age_hours' must not be negative",
        "unknown priority 'P9'",
        "field 'tags' must contain only strings",
    ]


# ---------------------------------------------------------------- load_exports
def test_load_exports_sample(sample_exports, sla_hours):
    paths = sorted(sample_exports.glob("*.json"))

    tickets, rejections = load_exports(paths, sla_hours=sla_hours)

    assert len(tickets) == 11
    assert all(isinstance(ticket, Ticket) for ticket in tickets)
    assert tickets[0].team == "platform"  # normalised from "Platform"
    assert [(r.file, r.record, r.id) for r in rejections] == [
        ("tickets-2026-10-20.json", 2, None),
        ("tickets-2026-10-20.json", 3, "INC-3011"),
        ("tickets-2026-10-20.json", 4, "INC-3012"),
        ("tickets-2026-10-20.json", 5, "INC-3013"),
        ("tickets-2026-10-21.json", None, None),
        ("tickets-legacy.json", None, None),
    ]


def test_load_exports_continues_after_a_bad_file(tmp_path, make_record, sla_hours):
    bad = tmp_path / "a-bad.json"
    bad.write_text("[{", encoding="utf-8")
    good = write_json(tmp_path / "b-good.json", [make_record()])

    tickets, rejections = load_exports([bad, good], sla_hours=sla_hours)

    assert [ticket.id for ticket in tickets] == ["INC-9001"]
    assert len(rejections) == 1
    assert isinstance(rejections[0], Rejection)
    assert rejections[0].file == "a-bad.json"
    assert rejections[0].record is None
