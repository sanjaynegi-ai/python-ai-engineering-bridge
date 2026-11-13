"""Acceptance tests for the command line, and against the real fake server. Do not edit."""

import httpx
import pytest

from asset_lookup.cli import main
from asset_lookup.client import InventoryClient
from asset_lookup.errors import AssetNotFound, InventoryAuthError, InventoryUnavailable


@pytest.fixture
def cli_env(clean_env):
    clean_env.setenv("INVENTORY_BASE_URL", "http://inventory.test")
    clean_env.setenv("INVENTORY_API_TOKEN", "cli-secret-token")
    return clean_env


# ---------------------------------------------------------------- command line
def test_show(cli_env, inventory, make_asset_json, capsys):
    inventory.get("/assets/db-03").respond(200, json=make_asset_json())

    assert main(["show", "db-03"]) == 0
    assert "Orders database replica" in capsys.readouterr().out


def test_show_unknown_asset(cli_env, inventory, capsys):
    inventory.get("/assets/nope").respond(404, json={"error": "asset 'nope' not found"})

    assert main(["show", "nope"]) == 1
    assert capsys.readouterr().err.startswith("error:")


def test_show_when_the_service_is_down(cli_env, inventory, capsys):
    inventory.get("/assets/db-03").mock(side_effect=httpx.ConnectError("refused"))

    assert main(["show", "db-03"]) == 3
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "cli-secret-token" not in captured.out + captured.err


def test_missing_token(clean_env, capsys):
    assert main(["show", "db-03"]) == 2
    assert "INVENTORY_API_TOKEN" in capsys.readouterr().err


def test_note(cli_env, inventory, capsys):
    inventory.post("/assets/db-03/notes").respond(201, json={"id": 3})

    assert main(["note", "db-03", "Disk replaced", "--ticket", "INC-3004"]) == 0
    assert "note 3" in capsys.readouterr().out


# ---------------------------------------------------------------- real HTTP
def test_against_the_fake_server(fake_server):
    with InventoryClient(fake_server, "test-token") as client:
        asset = client.get_asset("badge-zrh")
        platform = client.list_assets(team="platform", page_size=2)
        note_id = client.add_note("db-03", text="Checked from a test", ticket_id="INC-3004")

    assert asset.name == "Zürich depot badge readers"
    assert len(platform) == 5
    assert note_id >= 1


def test_errors_from_the_fake_server(fake_server):
    with InventoryClient(fake_server, "test-token", timeout_seconds=0.3) as client:
        with pytest.raises(AssetNotFound):
            client.get_asset("nope")
        with pytest.raises(InventoryUnavailable):
            client.get_asset("broken-01")
        with pytest.raises(InventoryUnavailable, match="timed out"):
            client.get_asset("slow-01")

    with InventoryClient(fake_server, "wrong-token") as client, pytest.raises(InventoryAuthError):
        client.get_asset("db-03")
