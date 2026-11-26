"""API tests for the initial FastAPI backend."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "AI Shopping & Deal-Finder API"


def test_create_search_returns_labelled_placeholder() -> None:
    response = client.post(
        "/api/v1/shopping/search",
        json={
            "query": "Apple iPhone 15 128GB",
            "budget_amount": "80000",
            "city": "Ujjain",
            "state": "Madhya Pradesh",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["mode"] == "placeholder"
    assert "not connected yet" in body["message"].lower()
    assert body["warnings"]


def test_local_search_requires_location() -> None:
    response = client.post(
        "/api/v1/shopping/search",
        json={"query": "Apple iPhone 15", "include_local_stores": True},
    )

    assert response.status_code == 422


def test_search_status_and_deals_are_retrievable() -> None:
    created = client.post(
        "/api/v1/shopping/search",
        json={"query": "Apple iPhone 15 128GB"},
    )
    search_id = created.json()["search_id"]

    status_response = client.get(f"/api/v1/shopping/search/{search_id}")
    deals_response = client.get(f"/api/v1/shopping/search/{search_id}/deals")

    assert status_response.status_code == 200
    assert deals_response.status_code == 200
    assert deals_response.json()["deals"] == []
    assert deals_response.json()["mode"] == "placeholder"


def test_unknown_search_returns_machine_readable_error() -> None:
    response = client.get("/api/v1/shopping/search/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SEARCH_NOT_FOUND"
