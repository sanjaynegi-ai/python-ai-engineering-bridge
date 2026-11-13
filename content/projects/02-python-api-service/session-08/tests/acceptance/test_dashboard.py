"""Acceptance tests for concurrent fetching and the dashboard (Milestone 4). Do not edit."""

import time
from datetime import UTC, datetime

import pytest

from incident_api.dashboard import (
    Dashboard,
    TeamAssets,
    build_dashboard,
    fetch_one_team,
    fetch_team_assets,
)
from incident_api.service import TicketService

pytestmark = pytest.mark.asyncio

TEAMS = ["database", "it-support", "network", "platform"]
GENERATED_AT = datetime(2026, 10, 22, 2, 0, tzinfo=UTC)


async def test_fetch_one_team(fake_inventory):
    async with fake_inventory.client() as client:
        result = await fetch_one_team(client, "network", deadline=1.0)

    assert isinstance(result, TeamAssets)
    assert result.team == "network"
    assert [asset.id for asset in result.assets] == ["vpn-ber"]
    assert result.error is None


async def test_fetch_team_assets_keeps_the_order_of_teams(fake_inventory):
    async with fake_inventory.client() as client:
        results = await fetch_team_assets(client, TEAMS, deadline=1.0)

    assert [result.team for result in results] == TEAMS
    assert [len(result.assets) for result in results] == [2, 1, 1, 3]


async def test_teams_are_fetched_concurrently(fake_inventory):
    async with fake_inventory.client() as client:
        await fetch_team_assets(client, TEAMS, deadline=1.0)

    assert fake_inventory.peak_in_flight == 4  # all four requests were waiting at once


async def test_concurrent_fetch_takes_about_one_latency_not_four(fake_inventory):
    fake_inventory.latency = 0.3

    async with fake_inventory.client() as client:
        started = time.perf_counter()
        await fetch_team_assets(client, TEAMS, deadline=5.0)
        elapsed = time.perf_counter() - started

    assert elapsed < 0.9  # sequential would take at least 4 x 0.3 = 1.2 seconds


async def test_one_failing_team_does_not_hide_the_others(fake_inventory):
    fake_inventory.failures["network"] = 500

    async with fake_inventory.client() as client:
        results = await fetch_team_assets(client, TEAMS, deadline=1.0)

    by_team = {result.team: result for result in results}
    assert by_team["network"].assets is None
    assert "500" in by_team["network"].error
    assert all(by_team[team].error is None for team in ["database", "it-support", "platform"])


async def test_a_slow_team_is_cut_off_at_its_deadline(fake_inventory):
    fake_inventory.delays["platform"] = 3.0

    async with fake_inventory.client() as client:
        started = time.perf_counter()
        results = await fetch_team_assets(client, TEAMS, deadline=0.3)
        elapsed = time.perf_counter() - started

    by_team = {result.team: result for result in results}
    assert by_team["platform"].assets is None
    assert by_team["platform"].error == "inventory did not answer within 0.3s"
    assert by_team["database"].error is None
    assert elapsed < 1.5  # nobody waited for the 3-second team


async def test_auth_failure_is_reported_for_every_team(fake_inventory):
    async with fake_inventory.client(token="wrong") as client:
        results = await fetch_team_assets(client, TEAMS, deadline=1.0)

    assert all(result.assets is None and "401" in result.error for result in results)


async def test_no_teams_means_no_requests(fake_inventory):
    async with fake_inventory.client() as client:
        assert await fetch_team_assets(client, [], deadline=1.0) == []

    assert fake_inventory.requests == []


async def test_unexpected_exceptions_are_not_swallowed():
    class BrokenClient:
        async def team_assets(self, team: str):
            raise ValueError("a bug, not an inventory problem")

    with pytest.raises(ValueError):
        await fetch_one_team(BrokenClient(), "network", deadline=1.0)
    with pytest.raises(ValueError):  # a bug must not come back as one of the results
        await fetch_team_assets(BrokenClient(), ["network", "platform"], deadline=1.0)


@pytest.fixture
def service(sample_exports, sla_hours) -> TicketService:
    return TicketService.from_exports(sorted(sample_exports.glob("*.json")), sla_hours=sla_hours)


async def test_dashboard_without_inventory(service):
    dashboard = await build_dashboard(service, None, deadline=1.0, generated_at=GENERATED_AT)

    assert isinstance(dashboard, Dashboard)
    assert [team.team for team in dashboard.teams] == TEAMS
    it_support = dashboard.teams[1]
    assert (it_support.open, it_support.breached, it_support.unassigned_open) == (2, 2, 2)
    assert it_support.oldest_open_hours == 200
    assert all(team.assets is None for team in dashboard.teams)
    assert {team.inventory_error for team in dashboard.teams} == {"inventory not configured"}


async def test_dashboard_with_inventory(service, fake_inventory):
    async with fake_inventory.client() as client:
        dashboard = await build_dashboard(service, client, deadline=1.0, generated_at=GENERATED_AT)

    database = dashboard.teams[0]
    assert database.team == "database"
    assert [asset.id for asset in database.assets] == ["db-03", "db-backup"]
    assert database.inventory_error is None
    assert dashboard.generated_at == GENERATED_AT
    assert fake_inventory.peak_in_flight == 4


async def test_dashboard_json_shape(service):
    dashboard = await build_dashboard(service, None, deadline=1.0, generated_at=GENERATED_AT)

    team = dashboard.model_dump(mode="json")["teams"][0]
    assert set(team) == {
        "team",
        "open",
        "breached",
        "unassigned_open",
        "oldest_open_hours",
        "assets",
        "inventory_error",
    }
