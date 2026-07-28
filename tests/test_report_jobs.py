def make_report_payload(scenarios=None):
    return {
        "cash": 1000,
        "portfolio_id": None,
        "scenarios": scenarios or ["market_down_25"],
        "holdings": [
            {
                "ticker": "AAPL",
                "quantity": 10,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "BND",
                "quantity": 10,
                "price": 80,
                "asset_class": "bond",
                "sector": "fixed income",
            },
        ],
    }


def test_create_report_job_returns_job_id_and_status(client):
    response = client.post("/api/reports", json=make_report_payload())

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "completed"


def test_get_report_job_status_returns_result(client):
    create_response = client.post("/api/reports", json=make_report_payload())
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/reports/{job_id}")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert data["result_json"]["starting_value"] == 2800
    assert data["result_json"]["results"][0]["scenario_name"] == "market_down_25"


def test_report_job_failed_state_is_stored(client):
    response = client.post(
        "/api/reports",
        json=make_report_payload(["made_up_scenario"]),
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]
    status_response = client.get(f"/api/reports/{job_id}")
    data = status_response.json()

    assert data["status"] == "failed"
    assert data["result_json"] is None
    assert "unknown scenario name" in data["error_message"]


def test_missing_report_job_returns_404(client):
    response = client.get("/api/reports/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "report job not found"