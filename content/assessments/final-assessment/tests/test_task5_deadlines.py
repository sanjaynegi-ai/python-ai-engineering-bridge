"""Task 5: swap deadlines. Do not edit."""

from datetime import UTC, date, datetime

from swap_desk.deadlines import hours_left, swap_deadline


def test_the_deadline_is_sunday_0900_utc():
    deadline = swap_deadline(date(2026, 11, 16))
    assert deadline == datetime(2026, 11, 15, 9, 0, tzinfo=UTC)
    assert deadline.tzinfo is not None


def test_hours_left_counts_down_to_the_deadline():
    week = date(2026, 11, 16)
    assert hours_left(week, datetime(2026, 11, 14, 9, 0, tzinfo=UTC)) == 24.0
    assert hours_left(week, datetime(2026, 11, 15, 10, 30, tzinfo=UTC)) == -1.5
