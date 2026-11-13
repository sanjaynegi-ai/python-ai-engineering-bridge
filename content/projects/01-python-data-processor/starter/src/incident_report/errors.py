"""Exceptions raised by the incident_report package."""


class ConfigError(Exception):
    """The configuration file is missing or invalid."""


class ExportError(Exception):
    """An export file cannot be read, or is not a JSON list."""
