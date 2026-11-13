"""Domain objects returned by the client."""

from dataclasses import dataclass, fields

from asset_lookup.errors import InventoryError


@dataclass(frozen=True)
class Asset:
    """One entry in the Asset Inventory."""

    id: str
    name: str
    type: str
    team: str
    environment: str
    criticality: str

    @classmethod
    def from_json(cls, data: object) -> "Asset":
        """Build an Asset from decoded JSON, or raise InventoryError if the shape is wrong."""
        if not isinstance(data, dict):
            raise InventoryError(f"expected an asset object, got {type(data).__name__}")
        values = {}
        for field in fields(cls):
            value = data.get(field.name)
            if not isinstance(value, str):
                raise InventoryError(f"asset field {field.name!r} is missing or not a string")
            values[field.name] = value
        return cls(**values)
