"""Task 5: swap deadlines. Its tests fail: find out why, and fix it."""

from datetime import date, datetime, time, timedelta


def swap_deadline(week: date) -> datetime:
    """The last moment a swap for `week` may be submitted: 24 hours before the week
    starts on Monday at 09:00 UTC, so Sunday 09:00 UTC. The result is timezone-aware."""
    starts = datetime.combine(week, time(9, 0))
    return starts - timedelta(days=1)


def hours_left(week: date, now: datetime) -> float:
    """Hours until the swap deadline for `week`; negative once it has passed."""
    return (swap_deadline(week) - now).seconds / 3600
