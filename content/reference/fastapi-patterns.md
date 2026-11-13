# FastAPI Patterns

FastAPI builds an HTTP API from typed Python functions: the type hints drive request parsing, validation, the response format and the documentation at `/docs`. Session 07 teaches it, and Projects 02 and 04 use it. This page collects the patterns the course relies on.

## One complete example

```python
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class TicketIn(BaseModel):  # the request body
    title: str = Field(min_length=3)
    team: str


class TicketOut(TicketIn):  # the response: what the client sees
    id: int


class DuplicateTicket(Exception):
    pass


class TicketService:  # business logic: knows nothing about HTTP
    def __init__(self) -> None:
        self._tickets: dict[int, TicketOut] = {}

    def add(self, ticket: TicketIn) -> TicketOut:
        if any(t.title == ticket.title for t in self._tickets.values()):
            raise DuplicateTicket(ticket.title)
        created = TicketOut(id=len(self._tickets) + 1, **ticket.model_dump())
        self._tickets[created.id] = created
        return created

    def get(self, ticket_id: int) -> TicketOut | None:
        return self._tickets.get(ticket_id)

    def find(self, team: str | None) -> list[TicketOut]:
        return [t for t in self._tickets.values() if team is None or t.team == team]


def get_service(request: Request) -> TicketService:
    return request.app.state.service


Service = Annotated[TicketService, Depends(get_service)]
tickets = APIRouter(prefix="/tickets", tags=["tickets"])


@tickets.post("", status_code=status.HTTP_201_CREATED)
def create(ticket: TicketIn, service: Service) -> TicketOut:
    return service.add(ticket)


@tickets.get("/{ticket_id}")
def read(ticket_id: int, service: Service) -> TicketOut:
    found = service.get(ticket_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such ticket")
    return found


@tickets.get("")
def search(
    service: Service, team: Annotated[str | None, Query(max_length=30)] = None
) -> list[TicketOut]:
    return service.find(team)


def duplicate(request: Request, error: DuplicateTicket) -> JSONResponse:
    return JSONResponse(
        status_code=409, content={"detail": f"duplicate ticket: {error}"}
    )


def create_app() -> FastAPI:
    app = FastAPI(title="Tickets")
    app.state.service = TicketService()
    app.include_router(tickets)
    app.add_exception_handler(DuplicateTicket, duplicate)
    return app


client = TestClient(create_app())
print(
    client.post("/tickets", json={"title": "VPN drops", "team": "network"}).status_code
)
print(client.post("/tickets", json={"title": "VPN drops", "team": "network"}).json())
print(client.post("/tickets", json={"title": "x", "team": "network"}).status_code)
print(client.get("/tickets/1").json(), client.get("/tickets/9").status_code)
print(client.get("/tickets", params={"team": "dns"}).json())
```

| Where the value comes from | How you declare it |
|---|---|
| The path: `/tickets/{ticket_id}` | A parameter with the same name: `ticket_id: int` |
| The query string: `?team=dns` | Any other simple parameter; add constraints with `Annotated[..., Query(...)]` |
| The JSON body | A Pydantic model parameter |
| Headers, cookies | `Annotated[str, Header()]`, `Cookie()` |
| Anything shared (a service, settings, a client) | `Depends(...)` |

## Status codes and errors

| Situation | Response |
|---|---|
| Created | `status_code=201` on the route |
| Invalid input (wrong type, constraint, missing field) | **422**, produced by FastAPI with a list of errors: no code needed |
| Not found | `raise HTTPException(404, "no such ticket")` |
| A domain error from the service | Raise your own exception there; map it to a status with `app.add_exception_handler` |
| A dependency is down | 503, with a short message; log the details |
| An unexpected exception | 500: FastAPI hides the details from the client (keep it that way) |

Keep error `detail` messages short and fixed. Never put tracebacks, internal hostnames or user data in them.

## Dependencies and testing

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class Clock:
    def hour(self) -> int:
        import datetime

        return datetime.datetime.now().hour


def get_clock() -> Clock:
    return Clock()


app = FastAPI()


@app.get("/greeting")
def greeting(clock: Annotated[Clock, Depends(get_clock)]) -> dict[str, str]:
    return {"greeting": "morning" if clock.hour() < 12 else "afternoon"}


class NineOClock(Clock):
    def hour(self) -> int:
        return 9


app.dependency_overrides[get_clock] = NineOClock  # tests swap the dependency
print(TestClient(app).get("/greeting").json())
app.dependency_overrides.clear()
```

## Startup, shutdown and shared resources

Create expensive or shared objects (an HTTP client, a database pool, a loaded index) **once**, in a lifespan function, and close them at shutdown:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http = httpx.AsyncClient(timeout=5)  # one client, shared by every request
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)

with TestClient(app) as client:  # entering the client runs the lifespan
    print(client.get("/docs").status_code, type(app.state.http).__name__)
```

## `def` or `async def`?

| Endpoint | When | Why |
|---|---|---|
| `def` | It calls synchronous code (most libraries, file I/O, a sync SDK) | FastAPI runs it in a thread pool, so it doesn't block other requests |
| `async def` | It only awaits async libraries (`httpx.AsyncClient`, async database drivers) | It runs on the event loop, with no thread |
| **Never** | `async def` that calls blocking code (`time.sleep`, a sync HTTP client) | It stalls every request on the server |

## Running it

| Command | For |
|---|---|
| `uv run fastapi dev` | Development, with reload (needs `[tool.fastapi] entrypoint = "package.api:app"` in `pyproject.toml`, or a path argument) |
| `uv run uvicorn package.api:app --reload` | The same with uvicorn directly |
| `uv run uvicorn --factory package.api:create_app` | When the app comes from a factory function |
| `http://127.0.0.1:8000/docs` | The interactive documentation |

## Common mistakes

| Mistake | Better |
|---|---|
| Business logic in the route | Routes translate HTTP; a service does the work |
| Returning the database or domain object directly | A response model, so you control what's exposed |
| A global client or connection created at import time | Create it in the lifespan; tests can replace it |
| Catching every exception in the route and returning 200 with an error field | Raise, and let handlers map exceptions to status codes |
| Testing against a running server | `TestClient`: in-process, no port |

## Further reading

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/), especially [dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/), [handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) and [testing](https://fastapi.tiangolo.com/tutorial/testing/).
- [Lifespan events](https://fastapi.tiangolo.com/advanced/events/) and [`async def` or `def`](https://fastapi.tiangolo.com/async/).
- [`pydantic-patterns.md`](pydantic-patterns.md) and [`async-await.md`](async-await.md).
