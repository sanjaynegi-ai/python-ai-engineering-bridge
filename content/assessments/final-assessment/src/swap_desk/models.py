"""Task 3: the swap request contract."""

from datetime import UTC, time
from typing import Literal

from pydantic import BaseModel

Team = Literal["platform", "database", "network", "it-support"]

# An on-call week starts on Monday at 09:00 UTC.
WEEK_START_TIME = time(9, 0, tzinfo=UTC)


class SwapRequest(BaseModel):
    """A request to swap an on-call week with a colleague.

    Fields and rules are in TASKS.md, Task 3.
    """

    # TODO Task 3


class StoredSwap(SwapRequest):
    """A SwapRequest the API has stored, with its id."""

    # TODO Task 3
