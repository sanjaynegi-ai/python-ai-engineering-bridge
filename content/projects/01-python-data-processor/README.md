# Project 01: Python Data Processor

**Built in:** Sessions 02–04 · **Checkpoint:** end of Session 04 (Milestone 1)

## What you build

`incident-report`, a command-line tool for the fictional Orbital Logistics on-call team. It reads a folder of nightly ticket exports, rejects unusable files and records with clear reasons, and writes a JSON report of open tickets, SLA breaches, unassigned work and recurring tags. Its exit code tells a scheduler whether anything was rejected.

The project grows over three sessions:

| Session | You build | Where |
|---|---|---|
| 02 | Cleaning, deduplication, grouping and summaries over in-memory records | `ticket_summary.py` (Session 02 workbook) |
| 03 | Configuration, file reading, JSON, validation, error handling and exit codes | `incident_report.py` (Session 03 workbook) |
| 04 | An installable `src/`-layout package with dataclasses, a pytest suite and Ruff | this project's [`starter/`](starter/README.md) (Session 04 workbook) |

## What it demonstrates

Collections and comprehensions · functions with keyword-only arguments · exceptions and chaining · `pathlib`, files and JSON · hand validation · modules and packages · dataclasses · type hints · pytest with fixtures and parametrize · Ruff.

## Getting started

<!-- until:2 -->
Sessions 02 and 03 build the first pieces in single files. The packaged project in `starter/` begins in Session 04, whose workbook explains how to copy it into your own folder and which code to move where.
<!-- /until:2 -->
<!-- release:2 -->
Follow the [Session 04 workbook](../../sessions/session-04/workbook/assignment.md). It explains how to copy `starter/` into your own folder, which code to move where, and the acceptance criteria.
<!-- /release:2 -->
<!-- release:3 -->

## Checkpoint

[`checkpoint/`](checkpoint/README.md) is a complete reference version of Project 01, published after the Project 01 deadline. Compare it with your own, and read its unit tests. Project 02 starts from it.
<!-- /release:3 -->

## Checkpoint criteria

Project 01 is complete when:

- `uv run pytest` passes: the 48 provided acceptance tests, unchanged, plus at least 12 unit tests of your own;
- `uv run incident-report` writes the report and exits with code `1` for the sample data;
- `uv run ruff check .` and `uv run ruff format --check .` pass;
- the work is committed and tagged `project-01`.

All data in this project is synthetic.
