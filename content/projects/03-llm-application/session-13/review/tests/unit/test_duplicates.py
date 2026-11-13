"""Tests for duplicate detection."""

from unittest.mock import patch

from incident_triage.duplicates import (
    DuplicateDetectorFactory,
    SequenceMatcherStrategy,
    find_duplicates,
    flag_duplicates,
    normalise,
    similarity,
)
from incident_triage.models import IncidentReport

VPN_1 = IncidentReport(id="RPT-1", text="The VPN keeps dropping in the Berlin office.")
VPN_2 = IncidentReport(id="RPT-2", text="VPN keeps dropping in our Berlin office!")
PRINTER = IncidentReport(id="RPT-3", text="Printer on floor 3 prints misaligned labels.")


def test_normalise_removes_punctuation_and_stopwords():
    assert normalise("The VPN is down!") == "vpn down"


def test_similarity_of_identical_text_is_one():
    assert similarity("VPN down", "VPN down") == 1.0


def test_similarity_is_between_zero_and_one():
    assert 0.0 <= similarity(VPN_1.text, PRINTER.text) <= 1.0


def test_find_duplicates_returns_a_list():
    assert isinstance(find_duplicates([VPN_1, VPN_2, PRINTER]), list)


def test_find_duplicates_finds_the_vpn_reports():
    pairs = find_duplicates([VPN_1, VPN_2, PRINTER])

    assert any(pair[:2] == ("RPT-1", "RPT-2") for pair in pairs)


def test_find_duplicates_with_mocked_similarity():
    with patch("incident_triage.duplicates.similarity", return_value=0.9):
        pairs = find_duplicates([VPN_1, PRINTER])

    assert len(pairs) > 0


def test_flag_duplicates_flags_the_second_report():
    assert "RPT-2" in flag_duplicates([VPN_1, VPN_2, PRINTER])


def test_factory_creates_sequence_strategy():
    assert isinstance(DuplicateDetectorFactory.create(), SequenceMatcherStrategy)
