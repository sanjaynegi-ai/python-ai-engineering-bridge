"""Acceptance tests for GET /dashboard and the shared client (workbook Milestone 5). Do not edit."""

import pytest
from fastapi.testclient import TestClient

from incident_api.api import create_app, get_inventory
from incident_api.inventory import InventoryClient

TEAMS = ["database", "it-support", "network", "platform"]


def test_dashboard_without_inventory_configured(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    teams = response.json()["teams"]
    assert [team["team"] for team in teams] == TEAMS
    assert all(team["assets"] is None for team in teams)
    assert {team["inventory_error"] for team in teams} == {"inventory not configured"}


@pytest.fixture
def app_with_fake_inventory(clean_env, sample_exports, fake_inventory):
    app = create_app()
    inventory = fake_inventory.client()
    app.dependency_overrides[get_inventory] = lambda: inventory
    yield app
    app.dependency_overrides.clear()


def test_dashboard_with_inventory(app_with_fake_inventory, fake_inventory):
    with TestClient(app_with_fake_inventory) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    platform = response.json()["teams"][3]
    assert platform["team"] == "platform"
    assert [asset["id"] for asset in platform["assets"]] == [
        "api-gw-01",
        "track-web",
        "ci-runner-02",
    ]
    assert platform["open"] == 2
    assert fake_inventory.peak_in_flight == 4


def test_inventory_problems_never_fail_the_request(app_with_fake_inventory, fake_inventory):
    for team in TEAMS:
        fake_inventory.failures[team] = 503

    with TestClient(app_with_fake_inventory) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert all("503" in team["inventory_error"] for team in response.json()["teams"])


def test_dashboard_uses_the_deadline_setting(clean_env, sample_exports, fake_inventory):
    clean_env.setenv("INCIDENT_INVENTORY_DEADLINE_SECONDS", "0.2")
    fake_inventory.delays["network"] = 2.0
    app = create_app()
    inventory = fake_inventory.client()
    app.dependency_overrides[get_inventory] = lambda: inventory

    with TestClient(app) as client:
        teams = {team["team"]: team for team in client.get("/dashboard").json()["teams"]}

    assert teams["network"]["inventory_error"] == "inventory did not answer within 0.2s"
    assert teams["database"]["inventory_error"] is None


def test_one_client_is_created_at_startup_and_closed_at_shutdown(clean_env, sample_exports):
    clean_env.setenv("INCIDENT_INVENTORY_TOKEN", "not-a-real-token")
    app = create_app()

    with TestClient(app):
        inventory = app.state.inventory
        assert isinstance(inventory, InventoryClient)
        assert not inventory._http.is_closed

    assert inventory._http.is_closed


def test_no_client_without_a_token(client):
    assert client.app.state.inventory is None


def test_dashboard_is_documented(client):
    openapi = client.get("/openapi.json").json()

    assert openapi["paths"]["/dashboard"]["get"]["tags"] == ["service"]
    assert {"Dashboard", "TeamDashboard", "Asset"} <= set(openapi["components"]["schemas"])


def test_earlier_endpoints_still_work(client):
    assert client.get("/health").json() == {"status": "ok", "tickets": 10, "rejected": 6}
    assert client.get("/tickets/INC-3004").status_code == 200


def test_dashboard_uses_the_client_created_at_startup(clean_env, sample_exports, fake_inventory):
    # A real token and an unreachable URL: only the shared client can answer.
    clean_env.setenv("INCIDENT_INVENTORY_TOKEN", "not-a-real-token")
    clean_env.setenv("INCIDENT_INVENTORY_BASE_URL", "http://inventory.invalid")
    clean_env.setenv("INCIDENT_INVENTORY_DEADLINE_SECONDS", "1")
    app = create_app()

    with TestClient(app) as client:
        real_client = app.state.inventory
        app.state.inventory = fake_inventory.client()  # swap the shared client after startup
        teams = client.get("/dashboard").json()["teams"]
        app.state.inventory = real_client  # so shutdown closes the original

    assert all(team["inventory_error"] is None for team in teams)
    assert len(fake_inventory.requests) == 4
