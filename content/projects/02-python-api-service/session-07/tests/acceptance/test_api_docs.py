"""Acceptance tests for the generated OpenAPI document and startup (Milestone 6). Do not edit."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from incident_api.api import app, create_app


@pytest.fixture
def openapi(client) -> dict:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


def test_title_and_paths(openapi):
    assert openapi["info"]["title"] == "Incident API"
    # Later sessions add endpoints, so check that these exist rather than that nothing else does
    assert {"/health", "/report", "/tickets", "/tickets/{ticket_id}"} <= set(openapi["paths"])


def test_ticket_routes_are_tagged(openapi):
    tickets = openapi["paths"]["/tickets"]

    assert tickets["get"]["tags"] == ["tickets"]
    assert tickets["post"]["tags"] == ["tickets"]
    assert openapi["paths"]["/tickets/{ticket_id}"]["get"]["tags"] == ["tickets"]


def test_create_documents_201_and_409(openapi):
    responses = openapi["paths"]["/tickets"]["post"]["responses"]

    assert {"201", "409", "422"} <= set(responses)
    assert "200" not in responses


def test_get_ticket_documents_404(openapi):
    assert "404" in openapi["paths"]["/tickets/{ticket_id}"]["get"]["responses"]


def test_list_documents_its_query_parameters(openapi):
    parameters = openapi["paths"]["/tickets"]["get"]["parameters"]

    assert {p["name"] for p in parameters} == {"team", "priority", "open_only", "limit", "offset"}
    assert {p["in"] for p in parameters} == {"query"}


def test_response_schemas_are_published(openapi):
    schemas = openapi["components"]["schemas"]

    assert {"Ticket", "TicketOut", "TicketPage", "Health", "Report"} <= set(schemas)
    assert "is_open" in schemas["TicketOut"]["properties"]


def test_module_level_app_exists_for_fastapi_dev():
    assert app.title == "Incident API"


def test_invalid_settings_stop_the_startup(clean_env):
    clean_env.setenv("INCIDENT_SLA_HOURS", '{"P1": 30, "P2": 24, "P3": 72, "P4": 168}')

    with pytest.raises(ValidationError), TestClient(create_app()):
        pass


def test_settings_can_be_passed_to_the_factory(clean_env, sample_exports):
    from incident_api.settings import Settings

    settings = Settings(input_dir=sample_exports, sla_hours={"P1": 1, "P2": 2, "P3": 3, "P4": 4})

    with TestClient(create_app(settings)) as client:
        assert client.get("/report").json()["totals"]["breached"] == 9
        assert client.get("/tickets/INC-3008").json()["breached"] is True  # P1, 3 hours
