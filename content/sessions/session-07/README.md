# Session 07: FastAPI

**Phase 2: Professional Python Applications** · **Project 02, stage 2**

## Session overview

In Session 05 you called an HTTP API, and in Session 06 you described data with Pydantic. This session works from the other side: you'll **serve** an API with **FastAPI**. Endpoints are typed Python functions; FastAPI reads their parameters from the path, query string and body, validates them with your Pydantic models, and turns return values and exceptions into HTTP responses, with OpenAPI documentation generated from the same code.

The workbook puts Project 02 behind HTTP. Other teams can look up, list and create tickets and read the report, while the command line keeps working on the same domain code.

## Why this matters

Nearly every AI application you'll build is exposed as an API: a retrieval service, an extraction endpoint, an agent behind a chat UI. FastAPI is a common choice for those in Python, and the RAG capstone in Sessions 14 and 15 is a FastAPI application.

The framework itself is quick to learn. The engineering judgment around it takes longer, and it's what this session practises: which status code for which failure, what belongs in a route and what in a service, how to keep internal fields out of responses, and how to test an API without a server.

## Prerequisites

**Knowledge:** Sessions 01–06. In particular, Session 05's HTTP status codes and clients, and Session 06's models, `ValidationError` and settings.

**Before the session:**

1. In the course repository, run `uv sync`. It adds FastAPI to the notebook kernel.
2. Finish the Session 06 workbook and tag it `session-06`. This session's workbook adds to that project.
3. Run `uv run python -c "from incident_api.models import Ticket; import json; print(json.dumps(Ticket.model_json_schema(), indent=2))"` in your project, if you haven't already. You'll see it again in `/docs`.

## Learning objectives

By the end of this session you will be able to:

1. **Implement** FastAPI endpoints with typed path and query parameters, request bodies and response models.
2. **Choose** status codes for success and failure (`201`, `404`, `409`, `422`), and **implement** them with `HTTPException` and exception handlers.
3. **Inject** settings and services with `Depends`, and **override** them in tests with `dependency_overrides`.
4. **Structure** an application into routers, API schemas and a service layer without HTTP, built by an app factory with a lifespan.
5. **Test** endpoints with `TestClient`, and **verify** the generated OpenAPI document.
6. **Explain** the limitations of in-memory state in a web service.


## Concepts covered

| Concept | Depth |
|---|---|
| `FastAPI`, route decorators, `TestClient` | Independent implementation |
| Path and query parameters, `Path`/`Query` constraints, query parameter models | Independent implementation |
| Request bodies, response models as return types, `status_code` | Independent implementation |
| `HTTPException`, exception handlers, `422` error bodies | Independent implementation |
| `Depends`, `Annotated` aliases, `dependency_overrides` | Independent implementation |
| `APIRouter`, service layer, app factory | Independent implementation |
| Lifespan (startup and shutdown), `app.state` | Working knowledge |
| OpenAPI, `/docs`, documenting error responses | Working knowledge |
| `fastapi dev` / `fastapi run`, Uvicorn and ASGI | Working knowledge |
| `def` versus `async def` endpoints | Awareness (Session 08) |



## Guided exercises

1. [`notebooks/01-concepts.ipynb`](notebooks/01-concepts.ipynb):
   - **First endpoint:** `TestClient`, and the framework comparison.
   - **Parameters:** predict three `422`s, and an unexpected `500`.
   - **Query parameter models:** a typo that returns wrong data, and how to refuse it.
   - **Response models:** a leaky endpoint, and the filtered version.
   - **Errors:** `HTTPException` and exception handlers.
   - **Dependencies:** settings, a service, an API-key guard, and overrides.
   - **Structure:** routers, an app factory, and a lifespan.
   - **Testing:** a small project tested with real pytest.
   - **Documentation:** reading the generated OpenAPI document.
2. [`notebooks/02-practice-quiz.ipynb`](notebooks/02-practice-quiz.ipynb): 10 self-check questions.

## Independent assignment

[**Workbook: Project 02 becomes a service**](workbook/assignment.md) (*Independent*: no AI coding assistant)

Add a `TicketService` without HTTP, API schemas, and five endpoints to your Session 06 project: health, report, list with filters and paging, get one, and create. `404`, `409` and `422` are each returned where they belong, and are documented in `/docs`. 63 new acceptance tests are provided, one file per milestone, and you write at least 10 of your own. The new files are in [`projects/02-python-api-service/session-07`](../../projects/02-python-api-service/README.md).

## Expected deliverables

- The `incident-api` project with `service.py`, `schemas.py` and `api.py`, tagged `session-07`.
- `uv run pytest` passing: 116 acceptance tests, unchanged, plus your own.
- `NOTES.md` with your design notes, the run-through observations and your reflection.

## Common mistakes

| Mistake | Instead |
|---|---|
| Returning the internal model | A response model; the return type filters what leaves |
| A missing resource returned as `null` or a `500` | `404`, from a domain exception and a handler |
| `HTTPException` in the service layer | Domain exceptions; map them in the API layer |
| `200` for a `POST` that creates | `status_code=201` |
| Business logic in route functions | A service layer, tested without HTTP |
| Building the service inside each endpoint | `Depends(get_service)`, created once at startup |
| `TestClient(app)` without `with` when the app has a lifespan | `with TestClient(app) as client:` |
| Overrides left in place after a test | Clear `dependency_overrides` in fixture teardown |
| Silently ignoring unknown query parameters | A filter model with `extra="forbid"` |
| Undocumented `404`/`409` | `responses={...}` on the route |

## Reading resources

Curated official documentation for this session: [`resources/references.md`](resources/references.md).

## Reflection questions

1. Which layer should decide that a duplicate ticket is a `409`: the model, the service, the route, or a handler? Why?
2. What did the service layer cost you in this assignment, and what did it buy you?
3. Your API keeps data in memory. What would break first if three teams started using it tomorrow?
4. How is FastAPI's dependency injection different from the container you use in your main language, and which do you prefer for testing?

## Interview questions

Practise answering these out loud and support each answer with clear engineering reasoning:

1. Walk through what happens when a request reaches a FastAPI endpoint.
2. What's the difference between `422` and `400`, and between `404` and `409`?
3. How do you stop internal fields appearing in API responses?
4. How does dependency injection work in FastAPI, and how do you use it in tests?
5. Where would you put a business rule such as "closed tickets need a resolution", and why?
6. What's the difference between `def` and `async def` endpoints in FastAPI?
7. How would you structure a FastAPI service that several developers work on?

## Next-session preparation

**Session 08: Asynchronous Python** explains `async` and `await`, the event loop, and concurrent HTTP calls with `httpx.AsyncClient`. In the workbook, the incident service will enrich tickets with data from the Asset Inventory API from Session 05, calling it concurrently.

Before the session:

- Finish this workbook and tag it `session-07`.
- Have your Session 05 `asset-lookup` project at hand; its client is the starting point for the asynchronous version.
- Reread Part 9 of this session's concepts notebook: `def` versus `async def` is where Session 08 starts.

---

<!-- skillup-branding:start -->
## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center">
  <img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="#SkillUpWithSanjay logo" width="60">
</p>

<p align="center">
  <strong>#SkillUpWithSanjay</strong><br>
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
<!-- skillup-branding:end -->
