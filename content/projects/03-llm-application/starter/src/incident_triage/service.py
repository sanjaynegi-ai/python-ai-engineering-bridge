"""Triage a batch of reports, keeping going when individual reports fail."""

from collections.abc import Iterable

from incident_triage.llm import Triager
from incident_triage.models import IncidentReport, TriageRun


def triage_all(
    triager: Triager,
    reports: Iterable[IncidentReport],
    *,
    input_usd_per_million: float | None = None,
    output_usd_per_million: float | None = None,
) -> TriageRun:
    """One outcome per report, in order. Workbook Milestone 4.

    A problem with one report (refusal, invalid output, the provider unavailable)
    is recorded and the run continues. A configuration problem stops the run,
    because every later request would fail the same way.
    """
    raise NotImplementedError
