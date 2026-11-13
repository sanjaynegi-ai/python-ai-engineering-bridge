"""An asynchronous client for the Asset Inventory API (the async version of Session 05's).

Workbook Milestone 3. The constructor and the closing methods are provided.
"""

import httpx

# Milestone 3: class Asset(BaseModel)
#   Frozen; id, name, type, team, environment and criticality, all str.
#   Unknown fields are ignored (the default).


class InventoryClient:
    """Talks HTTP to the Asset Inventory; callers get Assets and InventoryErrors back.

    One client is shared by every request: create it once, and close it with
    `await client.aclose()` (or `async with`) so its connections are released.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout_seconds: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=timeout_seconds,
            transport=transport,
        )

    # Milestone 3: the classmethod from_settings(settings, *, transport=None)
    #   Returns None when settings.inventory_token is None; otherwise a client for
    #   inventory_base_url, with the token's secret value and inventory_timeout_seconds.

    async def __aenter__(self) -> "InventoryClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    # Milestone 3: async def team_assets(self, team, *, page_size=50) -> list[Asset]
    #   GET /assets?team=...&page=...&page_size=..., following pagination one page at a
    #   time, as in Session 05. Raise InventoryAuthError for 401/403, InventoryUnavailable
    #   for timeouts, connection failures and 5xx, and InventoryError for any other
    #   unusable answer (another status, invalid JSON, a page or asset of the wrong shape).
