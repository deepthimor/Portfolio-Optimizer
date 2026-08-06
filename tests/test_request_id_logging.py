from backend.services.logging_utils import get_request_id


def test_health_response_includes_request_id_header(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_health_response_reuses_incoming_request_id(client):
    response = client.get(
        "/health",
        headers={"X-Request-ID": "test-request-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_get_request_id_has_safe_default_outside_request_context():
    assert get_request_id() == "no-request-id"