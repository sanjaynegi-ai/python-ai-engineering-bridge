"""Fixtures shared by every test in this folder and below it."""

import importlib.util
import threading
from pathlib import Path

import pytest
import respx

BASE_URL = "http://inventory.test"
TOKEN = "test-token"
SERVER_FILE = Path(__file__).parents[1] / "fake_inventory_server.py"


@pytest.fixture
def make_asset_json():
    """A factory: call it to get the JSON for a valid asset, with any fields overridden."""

    def _make_asset_json(**overrides) -> dict:
        asset = {
            "id": "db-03",
            "name": "Orders database replica",
            "type": "database",
            "team": "database",
            "environment": "production",
            "criticality": "high",
        }
        asset.update(overrides)
        return asset

    return _make_asset_json


@pytest.fixture
def inventory():
    """A respx router for BASE_URL. Any request to a route you didn't define fails the test."""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
def client():
    """An InventoryClient pointed at BASE_URL, closed after the test."""
    from asset_lookup.client import InventoryClient

    with InventoryClient(BASE_URL, TOKEN, timeout_seconds=2.0) as inventory_client:
        yield inventory_client


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No INVENTORY_* variables, and an empty working folder, so no real .env is read."""
    for name in ("INVENTORY_BASE_URL", "INVENTORY_API_TOKEN", "INVENTORY_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


@pytest.fixture
def fake_server(clean_env):
    """The real fake_inventory_server.py, on a free local port, for integration tests."""
    clean_env.setenv("INVENTORY_API_TOKEN", TOKEN)
    spec = importlib.util.spec_from_file_location("fake_inventory_server", SERVER_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SLOW_SECONDS = 1.0
    server = module.make_server(port=0)  # port 0: the OS picks a free port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host}:{port}"
    server.shutdown()
    server.server_close()
