"""A rule-based triager: no LLM, no network, no cost.

It's a baseline. Use it to run the whole application without an API key, and to
compare the LLM's triage against simple keyword rules.
"""

from incident_triage.models import IncidentReport, Triage, TriageResult, Usage

TEAM_KEYWORDS = {
    "database": ("database", "db-", "replica", "backup", "sql"),
    "network": ("vpn", "dns", "network", "wifi", "wi-fi", "connectivity"),
    "it-support": ("laptop", "badge", "printer", "password", "account", "keyboard"),
    "platform": ("api", "website", "checkout", "deploy", "gateway", "tracking"),
}
P1_WORDS = ("down for everyone", "outage", "all customers", "data loss", "breach")
P2_WORDS = ("slow", "timeout", "intermittent", "degraded", "failing", "fails")


class KeywordTriager:
    """Deterministic: the same report always gets the same triage."""

    model = "keyword-rules"

    def triage(self, report: IncidentReport) -> Triage:
        text = report.text.lower()
        team = next(
            (name for name, words in TEAM_KEYWORDS.items() if any(w in text for w in words)),
            "unknown",
        )
        if any(word in text for word in P1_WORDS):
            priority, category = "P1", "outage"
        elif any(word in text for word in P2_WORDS):
            priority, category = "P2", "degradation"
        else:
            priority, category = "P3", "other"
        first_line = report.text.strip().splitlines()[0]
        summary = first_line if len(first_line) <= 160 else first_line[:157] + "..."
        result = TriageResult(
            priority=priority,
            team=team,
            category=category,
            affected_system=None,
            summary=summary,
            tags=[team] if team != "unknown" else [],
        )
        return Triage(result=result, model=self.model, usage=Usage(input_tokens=0, output_tokens=0))
