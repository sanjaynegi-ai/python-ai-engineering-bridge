"""Configuration from environment variables, and an optional .env file.

Workbook Milestone 2.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class Settings:
    base_url: str
    token: str = field(repr=False)  # never shown in logs or tracebacks
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Read settings from `env`; if None, from the process environment plus ./.env.

    Variables:
      INVENTORY_API_TOKEN        required; blank counts as missing
      INVENTORY_BASE_URL         default DEFAULT_BASE_URL; strip spaces and trailing "/"
      INVENTORY_TIMEOUT_SECONDS  default DEFAULT_TIMEOUT_SECONDS; must be a positive number

    When env is None, load ./.env from the current working folder first, without
    overriding variables that are already set.

    Raises SettingsError, naming the variable, for a missing token or a bad timeout.
    """
    raise NotImplementedError
