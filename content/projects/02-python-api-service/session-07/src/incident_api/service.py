"""The service layer: ticket operations that know nothing about HTTP.

Workbook Milestone 2. Nothing in this module imports FastAPI. The API module
translates HTTP requests into calls on TicketService, and its results and
exceptions back into HTTP responses.
"""

from datetime import datetime
from pathlib import Path

from incident_api.models import Priority, Rejection, Report, Ticket


class TicketService:
    """Tickets held in memory, loaded from export files, plus tickets added later."""

    def __init__(
        self, tickets: list[Ticket], rejections: list[Rejection], *, sla_hours: dict[str, int]
    ) -> None:
        """Keep every valid record (for the report) and look tickets up by id.

        When an id appears more than once, the first record wins, as in the report.
        Store a copy of sla_hours as the public attribute `self.sla_hours`.
        """
        raise NotImplementedError

    @classmethod
    def from_exports(cls, paths: list[Path], *, sla_hours: dict[str, int]) -> "TicketService":
        """A service holding the tickets and rejections that load_exports finds in `paths`."""
        raise NotImplementedError

    @property
    def ticket_count(self) -> int:
        """The number of unique tickets."""
        raise NotImplementedError

    @property
    def rejection_count(self) -> int:
        raise NotImplementedError

    def get(self, ticket_id: str) -> Ticket:
        """The ticket with this id. Raises TicketNotFoundError, never KeyError."""
        raise NotImplementedError

    def find(
        self,
        *,
        team: str | None = None,
        priority: Priority | None = None,
        open_only: bool = False,
    ) -> list[Ticket]:
        """Unique tickets matching every given filter, in the order they were loaded or added.

        `team` is compared after stripping and lower-casing, like Ticket.team.
        """
        raise NotImplementedError

    def add(self, ticket: Ticket) -> Ticket:
        """Store a new ticket and return it. Raises DuplicateTicketError if the id exists."""
        raise NotImplementedError

    def is_breached(self, ticket: Ticket) -> bool:
        """Whether the ticket breaches this service's SLA."""
        raise NotImplementedError

    def report(self, *, generated_at: datetime) -> Report:
        """The report over every valid record and rejection, including added tickets."""
        raise NotImplementedError
