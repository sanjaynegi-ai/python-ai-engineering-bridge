"""Acceptance tests for the inventory settings and errors (workbook Milestone 2). Do not edit."""

import pytest
from pydantic import SecretStr, ValidationError

from incident_api.errors import InventoryAuthError, InventoryError, InventoryUnavailable
from incident_api.settings import Settings


def test_inventory_defaults(clean_env):
    settings = Settings()

    assert settings.inventory_base_url == "http://127.0.0.1:8765"
    assert settings.inventory_token is None
    assert settings.inventory_timeout_seconds == 5.0
    assert settings.inventory_deadline_seconds == 10.0


def test_inventory_settings_from_the_environment(clean_env):
    clean_env.setenv("INCIDENT_INVENTORY_BASE_URL", "http://inventory.test")
    clean_env.setenv("INCIDENT_INVENTORY_TOKEN", "not-a-real-token")
    clean_env.setenv("INCIDENT_INVENTORY_TIMEOUT_SECONDS", "2.5")
    clean_env.setenv("INCIDENT_INVENTORY_DEADLINE_SECONDS", "4")

    settings = Settings()

    assert settings.inventory_base_url == "http://inventory.test"
    assert settings.inventory_timeout_seconds == 2.5
    assert settings.inventory_deadline_seconds == 4.0
    assert isinstance(settings.inventory_token, SecretStr)
    assert settings.inventory_token.get_secret_value() == "not-a-real-token"


def test_token_never_appears_in_repr(clean_env):
    clean_env.setenv("INCIDENT_INVENTORY_TOKEN", "not-a-real-token")

    assert "not-a-real-token" not in repr(Settings())


@pytest.mark.parametrize(
    "name", ["INCIDENT_INVENTORY_TIMEOUT_SECONDS", "INCIDENT_INVENTORY_DEADLINE_SECONDS"]
)
@pytest.mark.parametrize("value", ["0", "-1", "soon"])
def test_non_positive_or_non_numeric_seconds_are_rejected(clean_env, name, value):
    clean_env.setenv(name, value)

    with pytest.raises(ValidationError):
        Settings()


def test_inventory_error_hierarchy():
    assert issubclass(InventoryUnavailable, InventoryError)
    assert issubclass(InventoryAuthError, InventoryError)
    assert not issubclass(InventoryAuthError, InventoryUnavailable)
