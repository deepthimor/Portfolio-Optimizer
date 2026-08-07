from backend.services.rate_limit import reset_rate_limit_state


def test_validation_error_response_is_user_friendly(client):
    response = client.post("/api/portfolio/analyze", json={})

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "invalid_request"
    assert data["message"] == "Please check your request fields and try again."
    assert "details" in data
    assert "request_id" in data


def test_rate_limit_returns_safe_429(client, monkeypatch):
    reset_rate_limit_state()
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")

    first_response = client.get("/health")
    second_response = client.get("/health")
    third_response = client.get("/health")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert third_response.status_code == 429

    data = third_response.json()

    assert data["error"] == "rate_limit_exceeded"
    assert data["message"] == "Too many requests. Please wait before trying again."
    assert "request_id" in data
    assert "X-Request-ID" in third_response.headers

    reset_rate_limit_state()