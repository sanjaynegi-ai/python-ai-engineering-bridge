"""Exceptions raised by the asset_lookup package."""


class SettingsError(Exception):
    """Required configuration is missing or invalid."""


class InventoryError(Exception):
    """Base class: an Asset Inventory request did not produce a usable answer."""


class AssetNotFound(InventoryError):
    """The asset does not exist (HTTP 404)."""


class InventoryAuthError(InventoryError):
    """The token was missing, wrong or not allowed (HTTP 401 or 403)."""


class InventoryUnavailable(InventoryError):
    """The service could not be reached, timed out, or failed (HTTP 5xx)."""
