"""A small, synchronous client for the Asset Inventory API.

Workbook Milestones 3-6. Read the API description in the README first.
"""

import httpx

from asset_lookup.models import Asset
from asset_lookup.settings import Settings


class InventoryClient:
    """Talks HTTP to the Asset Inventory; callers get Assets and InventoryErrors back.

    Error contract (see errors.py):
      AssetNotFound         the asset does not exist (404)
      InventoryAuthError    the token was refused (401 or 403)
      InventoryUnavailable  timeout, connection failure, or any 5xx; chain the cause
      InventoryError        anything else unexpected: another status, invalid JSON,
                            or JSON with the wrong shape

    Use it as a context manager so its connections are closed:

        with InventoryClient(base_url, token) as client:
            asset = client.get_asset("db-03")
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout_seconds: float = 5.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Create ONE httpx.Client with the base URL, the Authorization and Accept
        headers, the timeout and the (optional) transport."""
        raise NotImplementedError

    @classmethod
    def from_settings(
        cls, settings: Settings, *, transport: httpx.BaseTransport | None = None
    ) -> "InventoryClient":
        raise NotImplementedError

    def __enter__(self) -> "InventoryClient":
        raise NotImplementedError

    def __exit__(self, *exc_info: object) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def get_asset(self, asset_id: str) -> Asset:
        """GET /assets/{asset_id} -> Asset."""
        raise NotImplementedError

    def list_assets(self, *, team: str | None = None, page_size: int = 50) -> list[Asset]:
        """GET /assets, page by page, until every asset (optionally for one team) is collected."""
        raise NotImplementedError

    def add_note(self, asset_id: str, *, text: str, ticket_id: str | None = None) -> int:
        """POST /assets/{asset_id}/notes with {"text": ..., "ticket_id": ...}; return the new id."""
        raise NotImplementedError
