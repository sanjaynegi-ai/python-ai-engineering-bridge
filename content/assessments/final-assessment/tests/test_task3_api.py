"""Task 3: the swap request model and the API. Do not edit."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from swap_desk.api import create_app
from swap_desk.models import SwapRequest

VALID = {
    "requester": "Amara Osei",
    "colleague": "Chen Wei",
    "team": "network",
    "week": "2026-11-16",
    "submitted_at": "2026-11-10T14:00:00+00:00",
}


def test_a_valid_request_is_accepted():
    request = SwapRequest.model_validate(VALID)
    assert request.week.isoformat() == "2026-11-16"


@pytest.mark.parametrize(
    "change",
    [
        {"team": "marketing"},
        {"week": "2026-11-17"},  # a Tuesday
        {"colleague": "Amara Osei"},
        {"requester": "   "},
        {"submitted_at": "2026-11-10T14:00:00"},  # no time zone
        {"submitted_at": "2026-11-15T10:00:00+00:00"},  # 23 hours before Monday 09:00 UTC
    ],
)
def test_invalid_requests_are_rejected(change):
    with pytest.raises(ValidationError):
        SwapRequest.model_validate(VALID | change)


def test_post_then_get():
    client = TestClient(create_app())
    response = client.post("/swaps", json=VALID)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1
    assert created["requester"] == "Amara Osei"
    assert client.get("/swaps/1").json() == created


def test_an_invalid_request_is_422_and_not_stored():
    client = TestClient(create_app())
    assert client.post("/swaps", json=VALID | {"week": "2026-11-17"}).status_code == 422
    assert client.get("/swaps").json() == []


def test_list_filters_by_team():
    client = TestClient(create_app())
    client.post("/swaps", json=VALID)
    client.post("/swaps", json=VALID | {"team": "database"})
    assert [s["team"] for s in client.get("/swaps").json()] == ["network", "database"]
    assert [s["id"] for s in client.get("/swaps", params={"team": "database"}).json()] == [2]


def test_an_unknown_swap_is_404():
    assert TestClient(create_app()).get("/swaps/99").status_code == 404
