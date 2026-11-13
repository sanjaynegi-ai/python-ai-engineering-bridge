"""Acceptance tests for creating tickets and overriding dependencies (Milestone 5). Do not edit."""

import pytest
from fastapi.testclient import TestClient

from incident_api.api import create_app, get_service
from incident_api.models import Ticket
from incident_api.service import TicketService


def test_create_ticket_returns_201_and_the_normalised_ticket(client, make_record):
    record = make_record(id="INC-9001", team=" IT-Support ", tags=["Access", "badge", "access"])

    response = client.post("/tickets", json=record)

    assert response.status_code == 201
    body = response.json()
    assert (body["id"], body["team"]) == ("INC-9001", "it-support")
    assert body["tags"] == ["access", "badge"]
    assert (body["breached"], body["sla_hours"]) == (True, 24)


def test_created_ticket_can_be_read_back_and_is_counted(client, make_record):
    client.post("/tickets", json=make_record(id="INC-9001"))

    assert client.get("/tickets/INC-9001").status_code == 200
    assert client.get("/health").json()["tickets"] == 11
    assert client.get("/report").json()["totals"]["unique_tickets"] == 11


def test_duplicate_id_is_409_and_keeps_the_original(client, make_record):
    response = client.post("/tickets", json=make_record(id="INC-3001"))

    assert response.status_code == 409
    assert response.json() == {"detail": "ticket INC-3001 already exists"}
    assert client.get("/tickets/INC-3001").json()["team"] == "platform"


@pytest.mark.parametrize(
    ("overrides", "location"),
    [
        ({"id": "3004"}, ["body", "id"]),
        ({"priority": "P9"}, ["body", "priority"]),
        ({"age_hours": "12"}, ["body", "age_hours"]),  # strict, as in the export files
        ({"age_hours": -1}, ["body", "age_hours"]),
    ],
)
def test_invalid_ticket_is_422_with_the_field_location(client, make_record, overrides, location):
    response = client.post("/tickets", json=make_record(**overrides))

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [location]


def test_missing_required_field_is_422(client, make_record):
    record = make_record()
    del record["assignee"]

    response = client.post("/tickets", json=record)

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"


def test_body_that_is_not_json_is_422(client):
    response = client.post(
        "/tickets", content="not json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_failed_create_changes_nothing(client, make_record):
    client.post("/tickets", json=make_record(id="INC-9001", priority="P9"))

    assert client.get("/tickets/INC-9001").status_code == 404
    assert client.get("/health").json()["tickets"] == 10


def test_get_service_can_be_overridden(clean_env, make_record, sla_hours):
    fake = TicketService([Ticket.model_validate(make_record(id="INC-1"))], [], sla_hours=sla_hours)
    app = create_app()
    app.dependency_overrides[get_service] = lambda: fake

    with TestClient(app) as client:  # startup finds no exports in the empty folder
        assert client.get("/health").json() == {"status": "ok", "tickets": 1, "rejected": 0}
        assert client.get("/tickets/INC-1").status_code == 200
        client.post("/tickets", json=make_record(id="INC-2"))

    assert fake.ticket_count == 2
