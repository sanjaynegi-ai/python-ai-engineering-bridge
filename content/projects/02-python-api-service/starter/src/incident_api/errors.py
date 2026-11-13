"""Exceptions raised by the incident_api package.

Invalid tickets and invalid settings are reported by Pydantic's ValidationError;
only problems Pydantic can't see need their own exception.
"""


class ExportError(Exception):
    """An export file cannot be read, or is not a JSON list."""
