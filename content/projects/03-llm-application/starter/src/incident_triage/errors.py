"""Exceptions raised by the incident_triage package.

Callers see these, never the provider SDK's own exceptions, so that swapping the
provider (or the framework, in Session 10) doesn't change any error handling.
"""


class TriageError(Exception):
    """Base class: a report could not be triaged."""


class LLMConfigurationError(TriageError):
    """No key, a rejected key, an unknown model, or a request the provider refuses.

    Retrying won't help, and neither will moving on to the next report.
    """


class LLMUnavailable(TriageError):
    """The provider timed out, was unreachable, rate-limited us or failed (5xx),
    even after the SDK's retries. Another attempt later may succeed."""


class LLMRefusal(TriageError):
    """The model declined to answer."""


class LLMInvalidOutput(TriageError):
    """The model answered, but not with a valid TriageResult: invalid or truncated
    JSON, or values that break a business rule."""


class ReportFileError(Exception):
    """A reports file can't be read, or a line isn't a valid report."""
