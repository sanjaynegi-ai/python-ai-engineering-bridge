"""Acceptance tests for Rejection and load_exports (workbook Milestone 4). Do not edit."""

import pytest
from pydantic import ValidationError

from incident_api.loading import load_exports
from incident_api.models import Rejection, Ticket


def test_rejection_from_validation_error(make_record):
    record = make_record(id="INC-7", priority="P9", age_hours="12")
    with pytest.raises(ValidationError) as caught:
        Ticket.model_validate(record)

    rejection = Rejection.from_validation_error(caught.value, file="a.json", record=3, raw=record)

    assert (rejection.file, rejection.record, rejection.id) == ("a.json", 3, "INC-7")
    assert [problem.split(":")[0] for problem in rejection.problems] == ["priority", "age_hours"]


def test_rejection_for_a_record_that_is_not_an_object():
    with pytest.raises(ValidationError) as caught:
        Ticket.model_validate(["INC-1"])

    rejection = Rejection.from_validation_error(caught.value, file="a.json", record=0, raw=["x"])

    assert rejection.id is None
    assert len(rejection.problems) == 1
    assert rejection.problems[0].startswith("record:")


def test_file_level_rejection_defaults():
    rejection = Rejection(file="a.json", problems=["a.json: file not found"])

    assert rejection.record is None
    assert rejection.id is None


@pytest.fixture
def loaded(sample_exports):
    return load_exports(sorted(sample_exports.glob("*.json")))


def test_load_exports(loaded):
    tickets, rejections = loaded

    assert len(tickets) == 11
    assert all(isinstance(ticket, Ticket) for ticket in tickets)
    assert all(isinstance(rejection, Rejection) for rejection in rejections)
    assert [(r.file, r.record, r.id) for r in rejections] == [
        ("tickets-2026-10-20.json", 2, None),
        ("tickets-2026-10-20.json", 3, "INC-3011"),
        ("tickets-2026-10-20.json", 4, "INC-3012"),
        ("tickets-2026-10-20.json", 5, "INC-3013"),
        ("tickets-2026-10-21.json", None, None),
        ("tickets-legacy.json", None, None),
    ]


def test_rejection_problems_name_the_fields(loaded):
    _, rejections = loaded

    fields = [[problem.split(":")[0] for problem in r.problems] for r in rejections[:4]]
    assert fields == [["id"], ["age_hours"], ["priority", "tags"], ["age_hours"]]
    assert rejections[4].problems[0].startswith("tickets-2026-10-21.json: invalid JSON at line 21")
