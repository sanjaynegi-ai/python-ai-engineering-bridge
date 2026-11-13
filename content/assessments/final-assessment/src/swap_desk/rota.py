"""Task 2: the on-call rota, from assignment rows to rule breaches."""

from datetime import date


def on_call_weeks(assignments: list[dict[str, str]]) -> dict[str, list[date]]:
    """Each engineer's on-call weeks, sorted, without duplicates.

    Each row is {"engineer": "...", "week": "YYYY-MM-DD"}. Engineer names are stripped
    of surrounding spaces. Raises ValueError for a row without an engineer (missing,
    or only spaces), or with a week that isn't a valid ISO date. Doesn't modify the rows.
    """
    # TODO Task 2
    raise NotImplementedError


def longest_streak(weeks: list[date]) -> int:
    """The most consecutive weeks (exactly 7 days apart) in `weeks`, which may be unsorted
    and contain duplicates. 0 for no weeks."""
    # TODO Task 2
    raise NotImplementedError


def rule_breaches(assignments: list[dict[str, str]], max_consecutive: int = 2) -> list[str]:
    """Engineers on call for more than `max_consecutive` weeks in a row, sorted by name."""
    # TODO Task 2
    raise NotImplementedError
