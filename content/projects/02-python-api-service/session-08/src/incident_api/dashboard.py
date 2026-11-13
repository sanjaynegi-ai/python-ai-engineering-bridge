"""The on-call dashboard: ticket statistics per team, plus each team's assets.

Workbook Milestone 4. The models are provided; the three functions are yours.

The assets come from the Asset Inventory, one team at a time over HTTP. All teams
are fetched concurrently, each with its own deadline, so one slow or failing team
costs at most its deadline and never hides the other teams' results.
"""

from datetime import datetime

from pydantic import BaseModel

from incident_api.inventory import Asset, InventoryClient
from incident_api.service import TicketService


class TeamAssets(BaseModel):
    """One team's assets, or why they couldn't be fetched. Exactly one of the two is set."""

    team: str
    assets: list[Asset] | None = None
    error: str | None = None


class TeamDashboard(BaseModel):
    team: str
    open: int
    breached: int
    unassigned_open: int
    oldest_open_hours: int | None
    assets: list[Asset] | None
    inventory_error: str | None


class Dashboard(BaseModel):
    generated_at: datetime
    teams: list[TeamDashboard]


async def fetch_one_team(client: InventoryClient, team: str, *, deadline: float) -> TeamAssets:
    """One team's assets, within `deadline` seconds.

    Never raises for inventory problems: a timeout becomes the error
    "inventory did not answer within <deadline>s" (format the number with :g), and an
    InventoryError becomes its message. Any other exception is a bug: let it propagate.
    """
    raise NotImplementedError


async def fetch_team_assets(
    client: InventoryClient, teams: list[str], *, deadline: float
) -> list[TeamAssets]:
    """Every team's assets, fetched concurrently, in the order of `teams`."""
    raise NotImplementedError


async def build_dashboard(
    service: TicketService,
    client: InventoryClient | None,
    *,
    deadline: float,
    generated_at: datetime,
) -> Dashboard:
    """Teams in alphabetical order, with their ticket statistics and assets.

    The statistics are the report's per-team TeamStats. Without a client, every team's
    inventory_error is "inventory not configured" and nothing is fetched.
    """
    raise NotImplementedError
