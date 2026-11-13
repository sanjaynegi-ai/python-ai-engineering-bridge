# incident-report

The nightly incident report for the Orbital Logistics on-call team. Orbital Logistics is a fictional company, and all data in this project is synthetic.

The tool reads every ticket export in a folder, rejects files and records that can't be used (and says why), and writes a JSON report: open tickets, SLA breaches and unassigned work per team, plus the most common tags.

## Requirements

- [uv](https://docs.astral.sh/uv/) 0.13 or newer. uv installs Python 3.13 automatically if you don't have it.

## Setup

```bash
uv sync
```

This creates `.venv/` and installs the `incident_report` package into it in **editable** mode, so your changes to `src/` take effect without reinstalling.

## Usage

```bash
uv run incident-report               # uses ./config.json
uv run incident-report path/to/config.json
uv run python -m incident_report     # the same, run as a module
```

| Exit code | Meaning |
|---:|---|
| `0` | Report written; nothing was rejected |
| `1` | Report written, but some files or records were rejected (listed on stderr) |
| `2` | No report: the configuration is invalid, or there are no export files |

`config.json` sets the export folder, the output file and the SLA hours per priority. Paths are relative to the config file's folder.

## Project layout

```text
incident-report/
├── pyproject.toml          project metadata, the incident-report command, Ruff and pytest settings
├── uv.lock                 exact dependency versions
├── config.json             sample configuration
├── data/exports/           sample exports (synthetic)
├── src/incident_report/
│   ├── __init__.py         marks the package; holds __version__
│   ├── __main__.py         makes `python -m incident_report` work
│   ├── errors.py           ConfigError, ExportError
│   ├── models.py           Ticket, Rejection, Config dataclasses
│   ├── loading.py          config, export files, record validation
│   ├── summary.py          deduplication and per-team calculations
│   ├── report.py           building and writing the JSON report
│   └── cli.py              main(): arguments, exit codes, messages
└── tests/
    ├── conftest.py         shared fixtures
    ├── fixtures/exports/   test data (a copy, so tests never depend on data/)
    ├── acceptance/         provided tests; do not edit
    └── unit/               your own tests
```

## Development

```bash
uv run pytest                        # all tests
uv run pytest tests/unit -v          # just your unit tests, one line each
uv run ruff check .                  # lint
uv run ruff format .                 # format
```
