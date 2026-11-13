"""Fixtures shared by every test in this folder and below it."""

import asyncio
import os
import shutil
from pathlib import Path

import httpx
import pytest

FIXTURE_EXPORTS = Path(__file__).parent / "fixtures" / "exports"


@pytest.fixture
def sla_hours() -> dict[str, int]:
    return {"P1": 4, "P2": 24, "P3": 72, "P4": 168}


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No INCIDENT_* variables, and an empty working folder, so no real .env is read."""
    for name in list(os.environ):
        if name.upper().startswith("INCIDENT_"):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


@pytest.fixture
def sample_exports(tmp_path: Path) -> Path:
    """A private copy of the sample exports at tmp_path/data/exports (the default input_dir)."""
    target = tmp_path / "data" / "exports"
    shutil.copytree(FIXTURE_EXPORTS, target)
    return target


@pytest.fixture
def make_record():
    """A factory: call it to get a valid raw record, with any fields overridden."""

    def _make_record(**overrides) -> dict:
        record = {
            "id": "INC-9001",
            "title": "Badge readers offline at the Zürich depot",
            "team": "it-support",
            "priority": "P2",
            "status": "open",
            "age_hours": 28,
            "assignee": None,
            "tags": ["access"],
        }
        record.update(overrides)
        return record

    return _make_record


FAKE_ASSETS = [
    {"id": "api-gw-01", "name": "Public API gateway", "type": "service", "team": "platform",
     "environment": "production", "criticality": "high"},
    {"id": "track-web", "name": "Shipment tracking website", "type": "service",
     "team": "platform", "environment": "production", "criticality": "high"},
    {"id": "ci-runner-02", "name": "Build runner 2", "type": "server", "team": "platform",
     "environment": "internal", "criticality": "low"},
    {"id": "db-03", "name": "Orders database replica", "type": "database", "team": "database",
     "environment": "production", "criticality": "high"},
    {"id": "db-backup", "name": "Nightly backup store", "type": "storage", "team": "database",
     "environment": "production", "criticality": "medium"},
    {"id": "vpn-ber", "name": "Berlin office VPN concentrator", "type": "network",
     "team": "network", "environment": "production", "criticality": "medium"},
    {"id": "badge-zrh", "name": "Zürich depot badge readers", "type": "device",
     "team": "it-support", "environment": "site", "criticality": "medium"},
]  # fmt: skip


class FakeInventory:
    """An in-memory Asset Inventory, reached through httpx.MockTransport.

    Every request waits `latency` seconds with `await asyncio.sleep`, like a real
    network call, and the fake records how many requests were in flight at once.
    `failures` maps a team to an HTTP status, "timeout", "refused" or "garbage".
    `delays` maps a team to extra seconds of waiting.
    """

    token = "test-token"
    base_url = "http://inventory.test"

    def __init__(self) -> None:
        self.latency = 0.05
        self.failures: dict[str, int | str] = {}
        self.delays: dict[str, float] = {}
        self.requests: list[httpx.Request] = []
        self.in_flight = 0
        self.peak_in_flight = 0

    async def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        self.in_flight += 1
        self.peak_in_flight = max(self.peak_in_flight, self.in_flight)
        try:
            team = request.url.params.get("team")
            await asyncio.sleep(self.latency + self.delays.get(team, 0.0))
            if request.headers.get("Authorization") != f"Bearer {self.token}":
                return httpx.Response(401, json={"error": "missing or invalid token"})
            failure = self.failures.get(team)
            if failure == "timeout":
                raise httpx.ReadTimeout("read timed out", request=request)
            if failure == "refused":
                raise httpx.ConnectError("connection refused", request=request)
            if failure == "garbage":
                return httpx.Response(200, text="<html>not json</html>")
            if isinstance(failure, int):
                return httpx.Response(failure, json={"error": "simulated failure"})
            if request.url.path != "/assets":
                return httpx.Response(404, json={"error": "no such endpoint"})
            page = int(request.url.params.get("page", "1"))
            page_size = int(request.url.params.get("page_size", "3"))
            matching = [asset for asset in FAKE_ASSETS if asset["team"] == team]
            items = matching[(page - 1) * page_size : page * page_size]
            body = {"items": items, "page": page, "page_size": page_size, "total": len(matching)}
            return httpx.Response(200, json=body)
        finally:
            self.in_flight -= 1

    def client(self, *, token: str | None = None, timeout_seconds: float = 5.0):
        from incident_api.inventory import InventoryClient

        return InventoryClient(
            self.base_url,
            token or self.token,
            timeout_seconds=timeout_seconds,
            transport=httpx.MockTransport(self.handler),
        )


@pytest.fixture
def fake_inventory() -> FakeInventory:
    return FakeInventory()
