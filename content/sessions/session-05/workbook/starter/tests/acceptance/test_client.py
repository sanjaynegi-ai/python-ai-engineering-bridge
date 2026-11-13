"""Acceptance tests for asset_lookup.client. Do not edit.

The `inventory` fixture (tests/conftest.py) is a respx router: each test says
which requests it expects and what the "server" answers. No network is used.
"""

import json

import httpx
import pytest

from asset_lookup.client import InventoryClient
from asset_lookup.errors import (
    AssetNotFound,
    InventoryAuthError,
    InventoryError,
    InventoryUnavailable,
)
from asset_lookup.models import Asset
from asset_lookup.settings import Settings


# ---------------------------------------------------------------- get_asset
def test_get_asset(inventory, client, make_asset_json):
    route = inventory.get("/assets/db-03").respond(200, json=make_asset_json())

    asset = client.get_asset("db-03")

    assert asset == Asset.from_json(make_asset_json())
    assert route.call_count == 1


def test_requests_carry_the_token_and_ask_for_json(inventory, client, make_asset_json):
    route = inventory.get("/assets/db-03").respond(200, json=make_asset_json())

    client.get_asset("db-03")

    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-token"
    assert request.headers["Accept"] == "application/json"


def test_timeout_is_applied(inventory, make_asset_json):
    route = inventory.get("/assets/db-03").respond(200, json=make_asset_json())

    with InventoryClient("http://inventory.test", "t", timeout_seconds=1.5) as client:
        client.get_asset("db-03")

    timeouts = route.calls.last.request.extensions["timeout"]
    assert timeouts == {"connect": 1.5, "read": 1.5, "write": 1.5, "pool": 1.5}


def test_from_settings(inventory, make_asset_json):
    route = inventory.get("/assets/db-03").respond(200, json=make_asset_json())
    settings = Settings(base_url="http://inventory.test", token="from-settings")

    with InventoryClient.from_settings(settings) as client:
        client.get_asset("db-03")

    assert route.calls.last.request.headers["Authorization"] == "Bearer from-settings"


def test_unknown_asset(inventory, client):
    inventory.get("/assets/nope").respond(404, json={"error": "asset 'nope' not found"})

    with pytest.raises(AssetNotFound, match="nope"):
        client.get_asset("nope")


@pytest.mark.parametrize("status", [401, 403])
def test_refused_token(inventory, client, status):
    inventory.get("/assets/db-03").respond(status, json={"error": "missing or invalid token"})

    with pytest.raises(InventoryAuthError) as caught:
        client.get_asset("db-03")

    assert "test-token" not in str(caught.value)


@pytest.mark.parametrize("status", [500, 502, 503])
def test_server_errors(inventory, client, status):
    inventory.get("/assets/db-03").respond(status)

    with pytest.raises(InventoryUnavailable, match=str(status)):
        client.get_asset("db-03")


@pytest.mark.parametrize(
    "error",
    [httpx.ConnectTimeout("connect"), httpx.ReadTimeout("read"), httpx.ConnectError("refused")],
    ids=["connect-timeout", "read-timeout", "connect-error"],
)
def test_transport_failures(inventory, client, error):
    inventory.get("/assets/db-03").mock(side_effect=error)

    with pytest.raises(InventoryUnavailable) as caught:
        client.get_asset("db-03")

    assert caught.value.__cause__ is error


def test_invalid_json(inventory, client):
    inventory.get("/assets/db-03").respond(200, text="<html>maintenance</html>")

    with pytest.raises(InventoryError) as caught:
        client.get_asset("db-03")

    assert not isinstance(caught.value, InventoryUnavailable)
    assert isinstance(caught.value.__cause__, json.JSONDecodeError)


def test_wrong_shape(inventory, client):
    inventory.get("/assets/db-03").respond(200, json={"id": "db-03"})

    with pytest.raises(InventoryError):
        client.get_asset("db-03")


def test_unexpected_status(inventory, client):
    inventory.get("/assets/db-03").respond(418, text="I'm a teapot")

    with pytest.raises(InventoryError, match="418"):
        client.get_asset("db-03")


def test_client_is_closed_after_with(inventory, make_asset_json):
    inventory.get("/assets/db-03").respond(200, json=make_asset_json())

    with InventoryClient("http://inventory.test", "t") as client:
        client.get_asset("db-03")

    with pytest.raises(RuntimeError):
        client.get_asset("db-03")


# ---------------------------------------------------------------- list_assets
def paged(assets, page_size):
    """A respx side effect that serves `assets` page by page, like the real API."""

    def respond(request):
        page = int(request.url.params["page"])
        size = int(request.url.params["page_size"])
        assert size == page_size
        items = assets[(page - 1) * size : page * size]
        return httpx.Response(
            200, json={"items": items, "page": page, "page_size": size, "total": len(assets)}
        )

    return respond


def test_list_assets_follows_pagination(inventory, client, make_asset_json):
    assets = [make_asset_json(id=f"srv-{n}") for n in range(1, 6)]
    route = inventory.get("/assets").mock(side_effect=paged(assets, page_size=2))

    result = client.list_assets(page_size=2)

    assert [asset.id for asset in result] == ["srv-1", "srv-2", "srv-3", "srv-4", "srv-5"]
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2", "3"]


def test_list_assets_filters_by_team(inventory, client, make_asset_json):
    route = inventory.get("/assets").mock(side_effect=paged([make_asset_json()], page_size=50))

    client.list_assets(team="database")

    assert route.calls.last.request.url.params["team"] == "database"


def test_list_assets_without_team_sends_no_team(inventory, client):
    route = inventory.get("/assets").mock(side_effect=paged([], page_size=50))

    assert client.list_assets() == []
    assert "team" not in route.calls.last.request.url.params
    assert route.call_count == 1


# ---------------------------------------------------------------- add_note
def test_add_note(inventory, client):
    route = inventory.post("/assets/db-03/notes").respond(
        201, json={"id": 7, "asset_id": "db-03", "text": "Disk replaced", "ticket_id": "INC-3004"}
    )

    note_id = client.add_note("db-03", text="Disk replaced", ticket_id="INC-3004")

    assert note_id == 7
    assert json.loads(route.calls.last.request.content) == {
        "text": "Disk replaced",
        "ticket_id": "INC-3004",
    }


def test_add_note_rejected(inventory, client):
    inventory.post("/assets/db-03/notes").respond(422, json={"error": "'text' is required"})

    with pytest.raises(InventoryError, match="422") as caught:
        client.add_note("db-03", text="")

    assert not isinstance(caught.value, InventoryUnavailable)


def test_add_note_unknown_asset(inventory, client):
    inventory.post("/assets/nope/notes").respond(404, json={"error": "asset 'nope' not found"})

    with pytest.raises(AssetNotFound):
        client.add_note("nope", text="hello")
