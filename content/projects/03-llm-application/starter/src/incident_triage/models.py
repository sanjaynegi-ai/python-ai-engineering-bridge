"""Data contracts: incident reports in, triage results out."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["P1", "P2", "P3", "P4"]
Team = Literal["platform", "database", "network", "it-support", "unknown"]
Category = Literal["outage", "degradation", "security", "access", "hardware", "other"]


class IncidentReport(BaseModel):
    """One free-text report, as it arrives from email or chat."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^RPT-\d+$")
    text: str = Field(min_length=1)


class TriageResult(BaseModel):
    """What the LLM must return for one report.

    Workbook Milestone 2: replace this placeholder with the fields and rules in the
    workbook's table. Every field must be required, including nullable ones.
    """


class Usage(BaseModel):
    """Tokens billed for one request.

    Workbook Milestone 2: input_tokens and output_tokens (both int, 0 or more), frozen,
    and the method cost_usd(*, input_per_million, output_per_million) -> float.
    """


class Triage(BaseModel):
    """A successful triage: the result, the model that produced it, and what it cost."""

    model_config = ConfigDict(frozen=True)

    result: TriageResult
    model: str
    usage: Usage


class TriageOutcome(BaseModel):
    """One report's outcome in a run: a triage, or the reason there isn't one."""

    report_id: str
    triage: Triage | None = None
    error: str | None = None


class TriageRun(BaseModel):
    """Every outcome of a run, in input order, with token and cost totals."""

    outcomes: list[TriageOutcome]
    input_tokens: int
    output_tokens: int
    cost_usd: float | None  # None when prices aren't configured

    @property
    def failed(self) -> list[TriageOutcome]:
        return [outcome for outcome in self.outcomes if outcome.error is not None]
