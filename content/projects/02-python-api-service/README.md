# Project 02: Python API Service

**Built in:** Sessions 05–08 · **Checkpoint:** end of Session 08 (Milestone 2)

## What you build

`incident-api`, the incident reporting service for the fictional Orbital Logistics on-call team. It starts as Project 01's report with a Pydantic data layer, becomes an HTTP API that other teams call, and finally enriches tickets with data from the Asset Inventory service, concurrently.

| Session | You build | Where |
|---|---|---|
| 05 | An HTTP client for the Asset Inventory API, with mocked tests | the `asset-lookup` project (Session 05 workbook) |
| 06 | Pydantic models for tickets and the report; `pydantic-settings` for configuration | this project's [`starter/`](starter/README.md) (Session 06 workbook) |
| 07 | A FastAPI service in front of the same logic: a service layer, API schemas and five endpoints | the same project, plus the files in `session-07/` (Session 07 workbook) |
| 08 | An on-call dashboard: every team's assets, fetched concurrently from the Asset Inventory, with deadlines and partial failure | the same project, plus the files in `session-08/` (Session 08 workbook) |

The starter is built from the [Project 01 checkpoint](../01-python-data-processor/checkpoint/README.md), so it doesn't depend on how far you got with Project 01.

## What it demonstrates

Pydantic models and settings · validation error handling · HTTP clients · FastAPI · dependency injection · asynchronous I/O · logging · testing with fakes and mocks.

## Getting started

Follow the [Session 06 workbook](../../sessions/session-06/workbook/assignment.md). Sessions 07 and 08 don't have new starters: their workbooks have you copy a folder of new modules (with stubs) and new acceptance tests over your own project.
<!-- release:4 -->

Then follow the [Session 07](../../sessions/session-07/workbook/assignment.md) and [Session 08](../../sessions/session-08/workbook/assignment.md) workbooks, which use [`session-07/`](session-07/) and [`session-08/`](session-08/). Project 02 is complete at the end of Session 08.
<!-- /release:4 -->

All data in this project is synthetic.
