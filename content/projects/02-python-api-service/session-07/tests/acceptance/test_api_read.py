"""Acceptance tests for the read endpoints (workbook Milestone 4). Do not edit."""

import pytest


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "tickets": 10, "rejected": 6}


def test_list_tickets_first_page(client):
    response = client.get("/tickets")

    assert response.status_code == 200
    body = response.json()
    assert (body["total"], body["limit"], body["offset"]) == (10, 20, 0)
    assert [item["id"] for item in body["items"]] == [f"INC-{n}" for n in range(3001, 3011)]


def test_list_tickets_paging(client):
    body = client.get("/tickets", params={"limit": 3, "offset": 6}).json()

    assert body["total"] == 10
    assert [item["id"] for item in body["items"]] == ["INC-3007", "INC-3008", "INC-3009"]


def test_list_tickets_offset_past_the_end_is_an_empty_page(client):
    body = client.get("/tickets", params={"offset": 50}).json()

    assert (body["total"], body["items"]) == (10, [])


def test_list_tickets_filters(client):
    body = client.get("/tickets", params={"team": "Database", "open_only": "true"}).json()

    assert body["total"] == 4
    assert {item["team"] for item in body["items"]} == {"database"}
    assert all(item["is_open"] for item in body["items"])


def test_list_items_carry_derived_fields(client):
    items = client.get("/tickets", params={"priority": "P4"}).json()["items"]

    assert items == [
        {
            "id": "INC-3007",
            "title": items[0]["title"],
            "team": "it-support",
            "priority": "P4",
            "status": "open",
            "age_hours": 200,
            "assignee": None,
            "tags": [],
            "is_open": True,
            "breached": True,
            "sla_hours": 168,
        }
    ]


@pytest.mark.parametrize(
    ("params", "location"),
    [
        ({"limit": 0}, ["query", "limit"]),
        ({"limit": 500}, ["query", "limit"]),
        ({"offset": -1}, ["query", "offset"]),
        ({"priority": "P9"}, ["query", "priority"]),
        ({"open_only": "maybe"}, ["query", "open_only"]),
        ({"teem": "database"}, ["query", "teem"]),
    ],
)
def test_list_tickets_rejects_invalid_query_parameters(client, params, location):
    response = client.get("/tickets", params=params)

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [location]


def test_get_ticket(client):
    response = client.get("/tickets/INC-3004")

    assert response.status_code == 200
    assert response.json()["age_hours"] == 80  # the first record of a duplicated id
    assert response.json()["breached"] is True


def test_get_unknown_ticket_is_404_with_a_message(client):
    response = client.get("/tickets/INC-9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "ticket INC-9999 not found"}


def test_get_malformed_id_is_422_not_404(client):
    response = client.get("/tickets/3004")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "ticket_id"]


def test_report(client):
    response = client.get("/report")

    assert response.status_code == 200
    report = response.json()
    assert report["totals"] == {
        "valid_records": 11,
        "unique_tickets": 10,
        "open": 9,
        "breached": 6,
        "rejected": 6,
    }
    assert [breach["id"] for breach in report["breaches"]][:2] == ["INC-3007", "INC-3004"]
    assert len(report["rejected"]) == 6
    assert "generated_at" in report


def test_unknown_path_is_404(client):
    assert client.get("/incidents").status_code == 404
