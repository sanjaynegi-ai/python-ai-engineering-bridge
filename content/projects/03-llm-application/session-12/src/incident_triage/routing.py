"""Deciding what happens to each triaged report: page the on-call team, queue it, or
send it to a person for review.

This module holds the routing contract and the plain-Python router. The LangGraph
version of the same workflow goes in workflow.py; both must behave identically.

Session 12 workbook, Milestones 2 and 3.
"""

from collections.abc import Iterable
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from incident_triage.errors import (  # noqa: F401  (you'll need them in PlainRouter)
    LLMConfigurationError,
    LLMInvalidOutput,
    LLMRefusal,
    TriageError,
)
from incident_triage.llm import Triager
from incident_triage.models import IncidentReport, Team, Triage
from incident_triage.offline import KeywordTriager  # noqa: F401  (KeywordTriager.model)

Action = Literal["page", "queue", "review"]
DEFAULT_MAX_ATTEMPTS = 2  # LLM attempts per report when the output is invalid


class Dispatch(BaseModel):
    """Where a report goes. `team` is None when it goes to review."""

    model_config = ConfigDict(frozen=True)

    action: Action
    team: Team | None
    reasons: list[str]  # why it needs review; empty for page and queue


class Routing(BaseModel):
    """One report's journey through the workflow."""

    report_id: str
    triage: Triage | None  # None when the model refused
    error: str | None  # the LLM's last error, if there was one
    attempts: int  # calls to the primary triager
    path: list[str]  # the steps taken, in order: "triage", "fallback", "check", then the action
    dispatch: Dispatch


class RoutingRun(BaseModel):
    routings: list[Routing]

    def count(self, action: Action) -> int:
        return sum(1 for routing in self.routings if routing.dispatch.action == action)


class Router(Protocol):
    def route(self, report: IncidentReport) -> Routing: ...


def review_reasons(triage: Triage) -> list[str]:
    """The business rules a triage must pass before it's acted on automatically.

    Returns every rule it breaks, in this order; an empty list means it may be routed:

    1. "no owning team": the team is "unknown".
    2. "P1 without an affected system": a P1 whose affected_system is None.
    3. "security incident below P2": category "security" at P3 or P4.
    4. "high priority from keyword rules": a P1 or P2 made by the KeywordTriager
       (its `model` is KeywordTriager.model).
    """
    # TODO Milestone 2
    raise NotImplementedError


def dispatch_for(triage: Triage, reasons: list[str]) -> Dispatch:
    """Review if any rule is broken; otherwise page the team for P1, and queue everything else.

    A suggested helper: both routers can use it.
    """
    # TODO Milestone 2
    raise NotImplementedError


class PlainRouter:
    """The workflow as ordinary Python: a loop, a few ifs, and a fallback."""

    def __init__(
        self, triager: Triager, fallback: Triager, *, max_attempts: int = DEFAULT_MAX_ATTEMPTS
    ) -> None:
        """Raise ValueError if max_attempts is less than 1."""
        # TODO Milestone 3
        raise NotImplementedError

    def route(self, report: IncidentReport) -> Routing:
        """Triage the report, then decide where it goes. The workflow:

        - triage: call the primary triager.
          - LLMConfigurationError: let it propagate (it stops the run).
          - LLMRefusal: go straight to review, without a fallback.
          - LLMInvalidOutput: try again, up to max_attempts calls; then the fallback.
          - any other TriageError (unavailable): the fallback at once; the SDK has
            already retried.
        - fallback: triage with the fallback triager instead.
        - check: apply review_reasons.
        - then exactly one of page, queue or review.

        Record each step's name in `path`, in order, as the Routing docstring describes.
        """
        # TODO Milestone 3
        raise NotImplementedError


def route_all(router: Router, reports: Iterable[IncidentReport]) -> RoutingRun:
    """Route every report, in order. A configuration error stops the run."""
    return RoutingRun(routings=[router.route(report) for report in reports])
