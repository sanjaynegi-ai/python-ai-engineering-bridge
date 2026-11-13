"""Acceptance tests for the asynchronous InventoryClient (workbook Milestone 3). Do not edit."""

import httpx
import pytest

from incident_api.errors import InventoryAuthError, InventoryError, InventoryUnavailable
from incident_api.inventory import Asset, InventoryClient
from incident_api.settings import Settings

pytestmark = pytest.mark.asyncio  # every test in this file is a coroutine


async def test_team_assets_returns_asset_models(fake_inventory):
    async with fake_inventory.client() as client:
        assets = await client.team_assets("database")

    assert [asset.id for asset in assets] == ["db-03", "db-backup"]
    assert all(isinstance(asset, Asset) for asset in assets)
    assert assets[0].criticality == "high"


async def test_sends_the_token_and_the_team(fake_inventory):
    async with fake_inventory.client() as client:
        await client.team_assets("network")

    request = fake_inventory.requests[0]
    assert request.headers["Authorization"] == "Bearer test-token"
    assert request.url.path == "/assets"
    assert request.url.params["team"] == "network"


async def test_follows_pagination_one_page_at_a_time(fake_inventory):
    async with fake_inventory.client() as client:
        assets = await client.team_assets("platform", page_size=1)

    assert [asset.id for asset in assets] == ["api-gw-01", "track-web", "ci-runner-02"]
    assert [r.url.params["page"] for r in fake_inventory.requests] == ["1", "2", "3"]
    assert fake_inventory.peak_in_flight == 1  # each page depends on the previous one


async def test_team_without_assets_is_an_empty_list(fake_inventory):
    async with fake_inventory.client() as client:
        assert await client.team_assets("facilities") == []

    assert len(fake_inventory.requests) == 1


async def test_wrong_token_raises_auth_error(fake_inventory):
    async with fake_inventory.client(token="wrong") as client:
        with pytest.raises(InventoryAuthError):
            await client.team_assets("database")


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        (500, InventoryUnavailable),
        (503, InventoryUnavailable),
        ("timeout", InventoryUnavailable),
        ("refused", InventoryUnavailable),
        ("garbage", InventoryError),
        (418, InventoryError),
    ],
)
async def test_failures_become_inventory_errors(fake_inventory, failure, expected):
    fake_inventory.failures["database"] = failure

    async with fake_inventory.client() as client:
        with pytest.raises(expected) as caught:
            await client.team_assets("database")

    if expected is InventoryError:
        assert not isinstance(caught.value, InventoryUnavailable)


async def test_invalid_asset_in_a_page_is_an_inventory_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [{"id": "x"}], "total": 1})

    client = InventoryClient("http://inventory.test", "t", transport=httpx.MockTransport(handler))
    async with client:
        with pytest.raises(InventoryError):
            await client.team_assets("database")


async def test_unknown_asset_fields_are_ignored():
    def handler(request: httpx.Request) -> httpx.Response:
        item = {"id": "x-1", "name": "X", "type": "t", "team": "qa", "environment": "e",
                "criticality": "low", "owner_email": "someone@example.invalid"}  # fmt: skip
        return httpx.Response(200, json={"items": [item], "total": 1})

    client = InventoryClient("http://inventory.test", "t", transport=httpx.MockTransport(handler))
    async with client:
        assets = await client.team_assets("qa")

    assert assets[0].id == "x-1"
    assert "owner_email" not in assets[0].model_dump()


async def test_client_is_closed_after_async_with(fake_inventory):
    async with fake_inventory.client() as client:
        pass

    assert client._http.is_closed


async def test_from_settings_without_a_token_is_none(clean_env):
    assert InventoryClient.from_settings(Settings()) is None


async def test_from_settings_uses_url_token_and_timeout(clean_env, fake_inventory):
    settings = Settings(
        inventory_base_url=fake_inventory.base_url,
        inventory_token="test-token",
        inventory_timeout_seconds=1.5,
    )

    client = InventoryClient.from_settings(
        settings, transport=httpx.MockTransport(fake_inventory.handler)
    )
    async with client:
        assets = await client.team_assets("network")

    assert [asset.id for asset in assets] == ["vpn-ber"]
    assert str(fake_inventory.requests[0].url).startswith("http://inventory.test/assets")
    assert client._http.timeout.read == 1.5


async def test_asset_is_frozen():
    asset = Asset(id="a", name="A", type="t", team="qa", environment="e", criticality="low")

    with pytest.raises(ValueError):
        asset.team = "other"
