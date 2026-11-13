"""Task 2: the rota. Do not edit."""

from datetime import date

import pytest

from swap_desk.rota import longest_streak, on_call_weeks, rule_breaches

D = date.fromisoformat


def test_weeks_are_grouped_sorted_and_deduplicated():
    rows = [
        {"engineer": "Amara Osei", "week": "2026-11-16"},
        {"engineer": "Amara Osei", "week": "2026-11-02"},
        {"engineer": " Amara Osei ", "week": "2026-11-16"},
        {"engineer": "Chen Wei", "week": "2026-11-30"},
    ]
    assert on_call_weeks(rows) == {
        "Amara Osei": [D("2026-11-02"), D("2026-11-16")],
        "Chen Wei": [D("2026-11-30")],
    }


@pytest.mark.parametrize(
    "row",
    [
        {"week": "2026-11-02"},
        {"engineer": "  ", "week": "2026-11-02"},
        {"engineer": "A", "week": "2 Nov"},
    ],
)
def test_bad_rows_are_value_errors(row):
    with pytest.raises(ValueError):
        on_call_weeks([row])


def test_the_longest_streak_counts_consecutive_weeks():
    weeks = [D("2026-11-02"), D("2026-11-09"), D("2026-11-23"), D("2026-11-30"), D("2026-12-07")]
    assert longest_streak(weeks) == 3


def test_rule_breaches_on_the_sample_rota():
    import json
    from pathlib import Path

    rows = json.loads((Path(__file__).parents[1] / "data" / "rota.json").read_text("utf-8"))
    assert rule_breaches(rows) == ["Amara Osei", "Priya Raman"]
    assert rule_breaches(rows, max_consecutive=3) == []


def test_the_command_lists_the_engineers_who_break_the_rule(capsys):
    from pathlib import Path

    from swap_desk.cli import main

    rota = Path(__file__).parents[1] / "data" / "rota.json"
    assert main(["breaches", str(rota)]) == 1
    assert capsys.readouterr().out.splitlines() == ["Amara Osei", "Priya Raman"]
