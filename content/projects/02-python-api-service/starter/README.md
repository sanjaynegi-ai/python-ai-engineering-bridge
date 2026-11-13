# incident-api

The incident reporting service for the Orbital Logistics on-call team. Orbital Logistics is a fictional company, and all data in this project is synthetic.

This is **Project 02**. It starts from the Project 01 checkpoint and grows over four sessions:

| Session | What's added |
|---|---|
| 06 | Pydantic models for tickets and the report, and `pydantic-settings` for configuration (**this starter**) |
| 07 | A FastAPI service in front of the same logic |
| 08 | Asynchronous enrichment from the Asset Inventory API |

## Setup

```bash
uv sync
```

Settings are optional. To change a default, copy `.env.example` to `.env` and edit it, or set `INCIDENT_*` environment variables. `.env` is git-ignored.

## Usage

```bash
uv run incident-report                  # writes out/report.json
uv run incident-report --summary-only   # the same, without the list of rejected records
uv run python -m incident_api
```

| Exit code | Meaning |
|---:|---|
| `0` | Report written; nothing was rejected |
| `1` | Report written, but some files or records were rejected (listed on stderr) |
| `2` | No report: invalid settings, or no export files |

## Project layout

```text
incident-api/
├── .env.example            documented settings; copy to .env to change them
├── data/exports/           sample exports (synthetic)
├── src/incident_api/
│   ├── models.py           Ticket, Rejection and the report models (Pydantic)
│   ├── settings.py         Settings (pydantic-settings)
│   ├── loading.py          reading export files; validating records into Tickets
│   ├── summary.py          deduplication and per-team calculations (from Project 01)
│   ├── report.py           building and writing the report
│   ├── errors.py           ExportError
│   └── cli.py              the incident-report command
└── tests/
    ├── conftest.py
    ├── acceptance/         provided tests; do not edit
    └── unit/               your own tests
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```
