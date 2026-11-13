"""Reading configuration and export files, and validating raw records."""

import json
from pathlib import Path

from incident_report.errors import ConfigError, ExportError
from incident_report.models import Config, Rejection, Ticket

# The type each field of a raw ticket record must have. A tuple means "any of these".
FIELD_TYPES = {
    "id": str,
    "title": str,
    "team": str,
    "priority": str,
    "status": str,
    "age_hours": int,
    "assignee": (str, type(None)),
    "tags": list,
}


def load_config(path: Path) -> Config:
    """Read the JSON configuration; paths are relative to the config file's folder."""
    try:
        with open(path, encoding="utf-8") as file:
            raw = json.load(file)
    except FileNotFoundError as error:
        raise ConfigError(f"config file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"{path.name} is not valid JSON: {error.msg} (line {error.lineno})"
        ) from error

    if not isinstance(raw, dict):
        raise ConfigError(f"{path.name}: expected a JSON object at the top level")
    for key in ("input_dir", "output_file", "sla_hours"):
        if key not in raw:
            raise ConfigError(f"{path.name} is missing {key!r}")
    for key in ("input_dir", "output_file"):
        if not isinstance(raw[key], str):
            raise ConfigError(f"{path.name}: {key!r} must be a string")

    sla_hours = raw["sla_hours"]
    valid_hours = isinstance(sla_hours, dict) and all(
        isinstance(hours, int) and not isinstance(hours, bool) and hours > 0
        for hours in sla_hours.values()
    )
    if not valid_hours:
        raise ConfigError(f"{path.name}: 'sla_hours' must map priorities to positive integers")

    return Config(
        input_dir=path.parent / raw["input_dir"],
        output_file=path.parent / raw["output_file"],
        sla_hours=sla_hours,
    )


def read_export(path: Path) -> list:
    """Return the top-level list of one export file, without validating its records."""
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise ExportError(f"{path.name}: file not found") from error
    except UnicodeDecodeError as error:
        raise ExportError(f"{path.name}: not UTF-8 text") from error
    except json.JSONDecodeError as error:
        raise ExportError(
            f"{path.name}: invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error

    if not isinstance(data, list):
        raise ExportError(f"{path.name}: expected a list of tickets, got {type(data).__name__}")
    return data


def _type_names(expected: type | tuple[type, ...]) -> str:
    types = expected if isinstance(expected, tuple) else (expected,)
    return " or ".join("None" if t is type(None) else t.__name__ for t in types)


def validate_record(record: object, *, sla_hours: dict[str, int]) -> list[str]:
    """Return every problem with one raw record. An empty list means it is valid."""
    if not isinstance(record, dict):
        return ["record is not a JSON object"]

    problems = []
    for field, expected in FIELD_TYPES.items():
        if field not in record:
            problems.append(f"missing field {field!r}")
            continue
        value = record[field]
        # No field accepts booleans, and bool is a subclass of int, so reject it first.
        if isinstance(value, bool) or not isinstance(value, expected):
            actual = "None" if value is None else type(value).__name__
            problems.append(f"field {field!r} must be {_type_names(expected)}, got {actual}")

    age = record.get("age_hours")
    if isinstance(age, int) and not isinstance(age, bool) and age < 0:
        problems.append("field 'age_hours' must not be negative")
    priority = record.get("priority")
    if isinstance(priority, str) and priority not in sla_hours:
        problems.append(f"unknown priority {priority!r}")
    tags = record.get("tags")
    if isinstance(tags, list) and not all(isinstance(tag, str) for tag in tags):
        problems.append("field 'tags' must contain only strings")
    return problems


def load_exports(
    paths: list[Path], *, sla_hours: dict[str, int]
) -> tuple[list[Ticket], list[Rejection]]:
    """Read and validate every export, in order. Bad files and records become Rejections."""
    tickets: list[Ticket] = []
    rejections: list[Rejection] = []
    for path in paths:
        try:
            records = read_export(path)
        except ExportError as error:
            rejections.append(Rejection(path.name, None, None, (str(error),)))
            continue
        for index, record in enumerate(records):
            problems = validate_record(record, sla_hours=sla_hours)
            if problems:
                ticket_id = record.get("id") if isinstance(record, dict) else None
                rejections.append(Rejection(path.name, index, ticket_id, tuple(problems)))
            else:
                tickets.append(Ticket.from_record(record))
    return tickets, rejections
