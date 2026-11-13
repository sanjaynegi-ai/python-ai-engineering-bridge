# asset-lookup

A client and command-line tool for the **Asset Inventory API** of the fictional Orbital Logistics. The incident tooling uses it to find out which system a ticket is about, which team owns it, and how critical it is. All data is synthetic.

## Setup

```bash
uv sync
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

Edit `.env` and set `INVENTORY_API_TOKEN=local-dev-token`, the token the local fake server accepts. `.env` is git-ignored: never commit it.

## Running against the fake server

The real inventory belongs to another team, so this project ships a fake one. Start it in its own terminal and leave it running:

```bash
uv run python fake_inventory_server.py
```

Then, in a second terminal:

```bash
uv run asset-lookup show db-03
uv run asset-lookup list --team platform
uv run asset-lookup note db-03 "Disk replaced" --ticket INC-3004
```

| Exit code | Meaning |
|---:|---|
| `0` | Success |
| `1` | The asset doesn't exist, or the service gave an unusable answer |
| `2` | Configuration or usage problem (for example, no token) |
| `3` | The service is unavailable, timed out, or refused the token |

## The Asset Inventory API

Base URL from `INVENTORY_BASE_URL` (default `http://127.0.0.1:8765`). Every endpoint except `/health` needs the header `Authorization: Bearer <token>`; without a valid token it answers `401`.

| Request | Success | Errors |
|---|---|---|
| `GET /health` | `200 {"status": "ok"}` | |
| `GET /assets/{id}` | `200` an asset object | `404 {"error": ...}` |
| `GET /assets?page=1&page_size=3&team=platform` | `200 {"items": [assets], "page": 1, "page_size": 3, "total": 5}` | `400` for a bad page or page size (1 to 50) |
| `POST /assets/{id}/notes` with JSON `{"text": "...", "ticket_id": "INC-1"}` | `201` the created note, including its integer `"id"` | `404` unknown asset, `422` missing text |

An asset object:

```json
{"id": "db-03", "name": "Orders database replica", "type": "database",
 "team": "database", "environment": "production", "criticality": "high"}
```

For trying out error handling, the fake server has two special assets: `broken-01` always answers `500`, and `slow-01` waits 3 seconds before answering.

## Project layout

```text
asset-lookup/
├── fake_inventory_server.py   the local fake API (not part of the package)
├── .env.example               configuration template; copy to .env
├── src/asset_lookup/
│   ├── errors.py              SettingsError, InventoryError and its subclasses
│   ├── models.py              the Asset dataclass
│   ├── settings.py            load_settings(): environment and .env
│   ├── client.py              InventoryClient
│   └── cli.py                 the asset-lookup command
└── tests/
    ├── conftest.py            shared fixtures, including a respx router
    ├── acceptance/            provided tests; do not edit
    └── unit/                  your own tests
```

## Development

```bash
uv run pytest            # no network needed, except the local fake server the tests start themselves
uv run ruff check .
uv run ruff format .
```

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
