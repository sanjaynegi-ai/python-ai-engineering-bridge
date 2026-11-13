"""The HTTP API: routes, dependencies, error handling and the application factory.

Workbook Milestones 4-6. Run it with `uv run fastapi dev` and open
http://127.0.0.1:8000/docs. Routes stay thin: they validate HTTP input, call
TicketService and shape the response.

Provided: get_service, the /health route and create_app with its startup code.
Yours: the /report and /tickets routes, and the two exception handlers.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request

from incident_api import __version__
from incident_api.schemas import Health
from incident_api.service import TicketService
from incident_api.settings import Settings

logger = logging.getLogger(__name__)


def get_service(request: Request) -> TicketService:
    """The TicketService created at startup. Tests replace it with dependency_overrides."""
    return request.app.state.service


ServiceDep = Annotated[TicketService, Depends(get_service)]

router = APIRouter()
tickets = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/health", tags=["service"])
def health(service: ServiceDep) -> Health:
    return Health(tickets=service.ticket_count, rejected=service.rejection_count)


# Milestone 4: GET /report (on `router`, tagged "service")
# Milestone 4: GET /tickets and GET /tickets/{ticket_id} (on `tickets`)
# Milestone 5: POST /tickets (on `tickets`)
# Milestones 4 and 5: the handlers for TicketNotFoundError (404) and DuplicateTicketError (409)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application. Without settings, they're read from the environment at startup."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Everything before `yield` runs once, at startup; after it, at shutdown.
        active = settings or Settings()  # invalid settings stop the startup here
        paths = sorted(active.input_dir.glob("*.json"))
        if not paths:
            logger.warning("no .json export files in %s; starting empty", active.input_dir)
        app.state.service = TicketService.from_exports(paths, sla_hours=active.sla_hours)
        yield

    app = FastAPI(
        title="Incident API",
        version=__version__,
        description="Incident tickets and reports for the fictional Orbital Logistics on-call team",
        lifespan=lifespan,
    )
    app.include_router(router)
    app.include_router(tickets)
    # Milestones 4 and 5: register your exception handlers here, with app.add_exception_handler
    return app


app = create_app()
