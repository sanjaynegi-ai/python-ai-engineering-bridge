"""API schemas: the shapes of HTTP requests and responses.

Workbook Milestone 3. Requests to create a ticket use the Ticket model itself.
Responses use the models below, so the public contract can grow (or hide fields)
without changing the domain model.
"""

from typing import Literal

from pydantic import BaseModel

# Milestone 3: class TicketOut(BaseModel)
#   Ticket's eight fields (tags as a list of str), plus is_open, breached and
#   sla_hours, and the classmethod from_ticket(ticket, *, sla_hours).

# Milestone 3: class TicketPage(BaseModel)
#   total, limit, offset (int) and items (list of TicketOut).

# Milestone 3: class TicketFilters(BaseModel)
#   The query parameters of GET /tickets; unknown parameters are rejected.
#   team, priority, open_only, limit and offset: see the workbook's table.


class Health(BaseModel):
    """The body of GET /health. Provided."""

    status: Literal["ok"] = "ok"
    tickets: int
    rejected: int


class ErrorMessage(BaseModel):
    """The body of a 404 or 409 response, for the API documentation. Provided."""

    detail: str
