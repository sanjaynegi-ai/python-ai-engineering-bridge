"""Acceptance tests for asset_lookup.settings and asset_lookup.models. Do not edit."""

import dataclasses

import pytest

from asset_lookup.errors import InventoryError, SettingsError
from asset_lookup.models import Asset
from asset_lookup.settings import Settings, load_settings


# ---------------------------------------------------------------- settings
def test_load_settings_from_mapping():
    settings = load_settings(
        {
            "INVENTORY_BASE_URL": "http://inventory.test/",
            "INVENTORY_API_TOKEN": "abc",
            "INVENTORY_TIMEOUT_SECONDS": "2.5",
        }
    )

    assert settings == Settings(base_url="http://inventory.test", token="abc", timeout_seconds=2.5)


def test_load_settings_defaults():
    settings = load_settings({"INVENTORY_API_TOKEN": "abc"})

    assert settings.base_url == "http://127.0.0.1:8765"
    assert settings.timeout_seconds == 5.0


@pytest.mark.parametrize("token", [None, "", "   "])
def test_missing_token_is_an_error(token):
    env = {} if token is None else {"INVENTORY_API_TOKEN": token}

    with pytest.raises(SettingsError, match="INVENTORY_API_TOKEN"):
        load_settings(env)


@pytest.mark.parametrize("timeout", ["abc", "0", "-1"])
def test_bad_timeout_is_an_error(timeout):
    env = {"INVENTORY_API_TOKEN": "abc", "INVENTORY_TIMEOUT_SECONDS": timeout}

    with pytest.raises(SettingsError, match="INVENTORY_TIMEOUT_SECONDS"):
        load_settings(env)


def test_settings_repr_hides_the_token():
    settings = Settings(base_url="http://inventory.test", token="super-secret-value")

    assert "super-secret-value" not in repr(settings)


def test_load_settings_reads_dotenv_in_the_working_folder(clean_env, tmp_path):
    (tmp_path / ".env").write_text(
        "INVENTORY_API_TOKEN=from-dotenv\nINVENTORY_TIMEOUT_SECONDS=3\n", encoding="utf-8"
    )

    settings = load_settings()

    assert settings.token == "from-dotenv"
    assert settings.timeout_seconds == 3.0


def test_environment_variables_win_over_dotenv(clean_env, tmp_path):
    (tmp_path / ".env").write_text("INVENTORY_API_TOKEN=from-dotenv\n", encoding="utf-8")
    clean_env.setenv("INVENTORY_API_TOKEN", "from-environment")

    assert load_settings().token == "from-environment"


# ---------------------------------------------------------------- models
def test_asset_from_json(make_asset_json):
    asset = Asset.from_json(make_asset_json())

    assert asset == Asset(
        id="db-03",
        name="Orders database replica",
        type="database",
        team="database",
        environment="production",
        criticality="high",
    )


@pytest.mark.parametrize(
    "data",
    [
        ["db-03"],
        {"id": "db-03"},
        {
            "id": "db-03",
            "name": "x",
            "type": "database",
            "team": 7,
            "environment": "production",
            "criticality": "high",
        },
    ],
    ids=["list", "missing-fields", "team-not-a-string"],
)
def test_asset_from_bad_json(data):
    with pytest.raises(InventoryError):
        Asset.from_json(data)


def test_asset_is_frozen(make_asset_json):
    asset = Asset.from_json(make_asset_json())

    with pytest.raises(dataclasses.FrozenInstanceError):
        asset.team = "platform"
