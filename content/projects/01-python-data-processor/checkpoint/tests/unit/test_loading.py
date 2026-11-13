"""Unit tests for loading edge cases."""

import json

import pytest

from incident_report.errors import ExportError
from incident_report.loading import load_exports, read_export, validate_record


def test_empty_export_file_is_rejected(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ExportError, match="empty.json"):
        read_export(path)


def test_empty_list_is_a_valid_export(tmp_path):
    path = tmp_path / "none.json"
    path.write_text("[]", encoding="utf-8")

    assert read_export(path) == []


@pytest.mark.parametrize("value", [None, 1.5, [], "12"])
def test_age_hours_must_be_an_int(make_record, sla_hours, value):
    problems = validate_record(make_record(age_hours=value), sla_hours=sla_hours)

    assert len(problems) == 1
    assert problems[0].startswith("field 'age_hours' must be int")


def test_non_object_record_is_rejected_with_no_id(tmp_path, sla_hours):
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps(["not a ticket"]), encoding="utf-8")

    tickets, rejections = load_exports([path], sla_hours=sla_hours)

    assert tickets == []
    assert rejections[0].id is None
    assert rejections[0].problems == ("record is not a JSON object",)
