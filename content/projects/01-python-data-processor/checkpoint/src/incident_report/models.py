"""Domain objects: tickets, rejections and configuration."""

from dataclasses import dataclass
from pathlib import Path

CLOSED_STATUSES = frozenset({"resolved", "closed"})


@dataclass(frozen=True)
class Ticket:
    """One cleaned incident ticket."""

    id: str
    title: str
    team: str
    priority: str
    status: str
    age_hours: int
    assignee: str | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def from_record(cls, record: dict) -> "Ticket":
        """Build a normalised Ticket from a record that has passed validation."""
        assignee = (record["assignee"] or "").strip()
        return cls(
            id=record["id"],
            title=record["title"],
            team=record["team"].strip().lower(),
            priority=record["priority"],
            status=record["status"].strip().lower(),
            age_hours=record["age_hours"],
            assignee=assignee or None,
            tags=tuple(sorted({tag.lower() for tag in record["tags"]})),
        )

    @property
    def is_open(self) -> bool:
        return self.status not in CLOSED_STATUSES

    def is_breached(self, sla_hours: dict[str, int]) -> bool:
        return self.is_open and self.age_hours > sla_hours[self.priority]


@dataclass(frozen=True)
class Rejection:
    """A file or record that could not be used, and why."""

    file: str
    record: int | None
    id: str | None
    problems: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "record": self.record,
            "id": self.id,
            "problems": list(self.problems),
        }


@dataclass(frozen=True)
class Config:
    """Settings loaded from config.json."""

    input_dir: Path
    output_file: Path
    sla_hours: dict[str, int]
