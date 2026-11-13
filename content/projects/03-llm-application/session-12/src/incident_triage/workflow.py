"""The routing workflow as a LangGraph state graph.

It must behave exactly like PlainRouter in routing.py; the same contract tests run
against both. The graph makes the steps, the loop and the routes explicit: you can
draw it, stream it step by step, and see which node produced each change.

Session 12 workbook, Milestones 4 and 5.
"""

import operator  # noqa: F401  (for a reducer)
from typing import Annotated, Literal, TypedDict  # noqa: F401

from langgraph.graph import END, START, StateGraph  # noqa: F401
from langgraph.graph.state import CompiledStateGraph

from incident_triage.llm import Triager
from incident_triage.models import IncidentReport
from incident_triage.routing import DEFAULT_MAX_ATTEMPTS, Routing


class TriageState(TypedDict, total=False):
    """Everything the nodes share. Milestone 4: add the keys you need.

    The tests start the graph with three keys, so these must exist with these names:
    `report` (the IncidentReport), `attempts` (an int) and `path` (a list[str] that
    each node appends its own name to, through a reducer).
    """

    report: IncidentReport
    # TODO Milestone 4


def build_workflow(
    triager: Triager, fallback: Triager, *, max_attempts: int = DEFAULT_MAX_ATTEMPTS
) -> CompiledStateGraph:
    """The compiled graph, with six nodes named triage, fallback, check, page, queue and
    review, connected as the workbook's diagram shows. Declare the possible destinations
    of every conditional edge. Raise ValueError if max_attempts is less than 1.
    """
    # TODO Milestone 4
    raise NotImplementedError


class GraphRouter:
    """The Router interface, backed by the compiled graph."""

    def __init__(
        self, triager: Triager, fallback: Triager, *, max_attempts: int = DEFAULT_MAX_ATTEMPTS
    ) -> None:
        """Build the graph as self.graph, and set self.recursion_limit: the smallest limit
        that lets the longest possible path finish (Milestone 5)."""
        # TODO Milestone 5
        raise NotImplementedError

    def route(self, report: IncidentReport) -> Routing:
        """Run the graph with self.recursion_limit, and turn its final state into a Routing."""
        # TODO Milestone 5
        raise NotImplementedError
