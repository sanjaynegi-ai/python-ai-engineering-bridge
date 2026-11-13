"""Acceptance tests for TriageResult and Usage (workbook Milestone 2). Do not edit."""

import pytest
from pydantic import ValidationError

from incident_triage.models import IncidentReport, TriageResult, Usage


def triage(**overrides) -> dict:
    data = {
        "priority": "P2",
        "team": "network",
        "category": "degradation",
        "affected_system": "Berlin office VPN",
        "summary": "VPN connections in the Berlin office drop every few minutes.",
        "tags": ["vpn", "berlin"],
    }
    return data | overrides


def test_valid_triage():
    result = TriageResult.model_validate(triage())

    assert result.priority == "P2"
    assert result.team == "network"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("priority", "urgent"),
        ("priority", "p1"),
        ("team", "facilities"),
        ("category", "bug"),
        ("tags", "vpn"),
        ("summary", None),
    ],
)
def test_values_outside_the_contract_are_rejected(field, value):
    with pytest.raises(ValidationError):
        TriageResult.model_validate(triage(**{field: value}))


def test_every_field_is_required_even_nullable_ones():
    data = triage()
    del data["affected_system"]

    with pytest.raises(ValidationError):
        TriageResult.model_validate(data)
    assert TriageResult.model_validate(triage(affected_system=None)).affected_system is None


def test_json_schema_lists_every_field_as_required():
    # The contract: the model must always send every field, even when its value is null
    schema = TriageResult.model_json_schema()

    assert set(schema["required"]) == set(schema["properties"])
    assert len(schema["properties"]) == 6


def test_summary_is_stripped_and_limited():
    assert TriageResult.model_validate(triage(summary="  Short.  ")).summary == "Short."
    assert len(TriageResult.model_validate(triage(summary="x" * 160)).summary) == 160
    for bad in ["", "   ", "x" * 161]:
        with pytest.raises(ValidationError):
            TriageResult.model_validate(triage(summary=bad))


def test_blank_affected_system_becomes_none():
    assert TriageResult.model_validate(triage(affected_system="  ")).affected_system is None
    assert TriageResult.model_validate(triage(affected_system=" DNS ")).affected_system == "DNS"


def test_tags_are_cleaned_and_limited():
    result = TriageResult.model_validate(triage(tags=["VPN", " berlin ", "vpn", ""]))

    assert result.tags == ["berlin", "vpn"]
    with pytest.raises(ValidationError):
        TriageResult.model_validate(triage(tags=["a", "b", "c", "d", "e", "f"]))


def test_triage_result_is_frozen():
    result = TriageResult.model_validate(triage())

    with pytest.raises(ValidationError):
        result.priority = "P1"


def test_usage_cost():
    usage = Usage(input_tokens=2_000, output_tokens=500)

    assert usage.cost_usd(input_per_million=0.10, output_per_million=0.50) == pytest.approx(0.00045)
    assert usage.cost_usd(input_per_million=4.0, output_per_million=20.0) == pytest.approx(0.018)


def test_usage_rejects_negative_tokens():
    with pytest.raises(ValidationError):
        Usage(input_tokens=-1, output_tokens=0)


def test_incident_report_ids():
    assert IncidentReport(id="RPT-1001", text="x").id == "RPT-1001"
    with pytest.raises(ValidationError):
        IncidentReport(id="1001", text="x")
