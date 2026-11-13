"""A fake Asset Inventory API for local development. Standard library only.

Run it in its own terminal:

    uv run python fake_inventory_server.py                 # listens on http://127.0.0.1:8765
    uv run python fake_inventory_server.py --latency 0.5   # every request takes 0.5 s longer

Session 08 adds --latency, so that the cost of waiting on the network is easy to see.

It accepts the token in the INVENTORY_API_TOKEN environment variable (or in
.env), and falls back to "local-dev-token". All data is synthetic: Orbital
Logistics is a fictional company.

Endpoints
    GET  /health
    GET  /assets?team=&page=&page_size=      paginated list
    GET  /assets/{asset_id}                  one asset, or 404
    POST /assets/{asset_id}/notes            JSON {"text": ..., "ticket_id": ...} -> 201

Special asset ids, for trying out error handling
    broken-01   always answers 500
    slow-01     waits SLOW_SECONDS before answering
"""

import argparse
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8765
SLOW_SECONDS = 3.0
LATENCY_SECONDS = 0.0  # set from --latency

ASSETS = [
    {
        "id": "api-gw-01",
        "name": "Public API gateway",
        "type": "service",
        "team": "platform",
        "environment": "production",
        "criticality": "high",
    },
    {
        "id": "track-web",
        "name": "Shipment tracking website",
        "type": "service",
        "team": "platform",
        "environment": "production",
        "criticality": "high",
    },
    {
        "id": "ci-runner-02",
        "name": "Build runner 2",
        "type": "server",
        "team": "platform",
        "environment": "internal",
        "criticality": "low",
    },
    {
        "id": "db-03",
        "name": "Orders database replica",
        "type": "database",
        "team": "database",
        "environment": "production",
        "criticality": "high",
    },
    {
        "id": "db-backup",
        "name": "Nightly backup store",
        "type": "storage",
        "team": "database",
        "environment": "production",
        "criticality": "medium",
    },
    {
        "id": "vpn-ber",
        "name": "Berlin office VPN concentrator",
        "type": "network",
        "team": "network",
        "environment": "production",
        "criticality": "medium",
    },
    {
        "id": "dns-int",
        "name": "Internal DNS resolvers",
        "type": "network",
        "team": "network",
        "environment": "production",
        "criticality": "high",
    },
    {
        "id": "badge-zrh",
        "name": "Zürich depot badge readers",
        "type": "device",
        "team": "it-support",
        "environment": "site",
        "criticality": "medium",
    },
    {
        "id": "printer-wh4",
        "name": "Warehouse 4 label printers",
        "type": "device",
        "team": "it-support",
        "environment": "site",
        "criticality": "low",
    },
    {
        "id": "broken-01",
        "name": "Always fails",
        "type": "test",
        "team": "platform",
        "environment": "test",
        "criticality": "low",
    },
    {
        "id": "slow-01",
        "name": "Always slow",
        "type": "test",
        "team": "platform",
        "environment": "test",
        "criticality": "low",
    },
]
NOTES: list[dict] = []


def expected_token() -> str:
    token = os.environ.get("INVENTORY_API_TOKEN")
    env_file = Path(".env")
    if token is None and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("INVENTORY_API_TOKEN="):
                token = line.split("=", 1)[1].strip()
    return token or "local-dev-token"


class InventoryHandler(BaseHTTPRequestHandler):
    server_version = "FakeInventory/1.0"

    # -- helpers ---------------------------------------------------------------
    def send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def authorised(self) -> bool:
        if self.headers.get("Authorization") == f"Bearer {self.server.token}":
            return True
        self.send_json(401, {"error": "missing or invalid token"})
        return False

    def log_message(self, format: str, *args) -> None:  # one short line per request
        sys.stderr.write(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}\n")

    # -- routes ----------------------------------------------------------------
    def do_GET(self) -> None:
        time.sleep(LATENCY_SECONDS)  # a slow network or a busy service
        url = urlparse(self.path)
        parts = [part for part in url.path.split("/") if part]
        if parts == ["health"]:
            return self.send_json(200, {"status": "ok"})
        if not self.authorised():
            return None
        if parts == ["assets"]:
            return self.list_assets(parse_qs(url.query))
        if len(parts) == 2 and parts[0] == "assets":
            return self.get_asset(parts[1])
        return self.send_json(404, {"error": "no such endpoint"})

    def do_POST(self) -> None:
        parts = [part for part in urlparse(self.path).path.split("/") if part]
        if not self.authorised():
            return None
        if len(parts) == 3 and parts[0] == "assets" and parts[2] == "notes":
            return self.add_note(parts[1])
        return self.send_json(404, {"error": "no such endpoint"})

    def get_asset(self, asset_id: str) -> None:
        if asset_id == "broken-01":
            return self.send_json(500, {"error": "internal server error"})
        if asset_id == "slow-01":
            time.sleep(SLOW_SECONDS)
        for asset in ASSETS:
            if asset["id"] == asset_id:
                return self.send_json(200, asset)
        return self.send_json(404, {"error": f"asset {asset_id!r} not found"})

    def list_assets(self, query: dict[str, list[str]]) -> None:
        try:
            page = int(query.get("page", ["1"])[0])
            page_size = int(query.get("page_size", ["3"])[0])
        except ValueError:
            return self.send_json(400, {"error": "page and page_size must be integers"})
        if page < 1 or not 1 <= page_size <= 50:
            return self.send_json(400, {"error": "page must be >= 1, page_size 1..50"})
        team = query.get("team", [None])[0]
        matching = [a for a in ASSETS if team is None or a["team"] == team]
        start = (page - 1) * page_size
        items = matching[start : start + page_size]
        return self.send_json(
            200, {"items": items, "page": page, "page_size": page_size, "total": len(matching)}
        )

    def add_note(self, asset_id: str) -> None:
        if not any(asset["id"] == asset_id for asset in ASSETS):
            return self.send_json(404, {"error": f"asset {asset_id!r} not found"})
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"null")
        except json.JSONDecodeError:
            return self.send_json(400, {"error": "body must be JSON"})
        if not isinstance(body, dict) or not isinstance(body.get("text"), str) or not body["text"]:
            return self.send_json(422, {"error": "'text' is required"})
        note = {
            "id": len(NOTES) + 1,
            "asset_id": asset_id,
            "text": body["text"],
            "ticket_id": body.get("ticket_id"),
        }
        NOTES.append(note)
        return self.send_json(201, note)


class InventoryServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        # A client that gave up (for example after its timeout) closes the connection
        # before we answer. Report it in one line instead of a full traceback.
        sys.stderr.write(f"client {client_address[0]}:{client_address[1]} disconnected early\n")


def make_server(host: str = HOST, port: int = PORT) -> InventoryServer:
    server = InventoryServer((host, port), InventoryHandler)
    server.token = expected_token()
    return server


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description="A fake Asset Inventory API.")
    arguments.add_argument("--port", type=int, default=PORT)
    arguments.add_argument("--latency", type=float, default=0.0, help="extra seconds per request")
    options = arguments.parse_args()
    LATENCY_SECONDS = options.latency
    server = make_server(port=options.port)
    print(
        f"Fake Asset Inventory on http://{HOST}:{options.port}, "
        f"latency {LATENCY_SECONDS:g}s  (Ctrl+C to stop)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
