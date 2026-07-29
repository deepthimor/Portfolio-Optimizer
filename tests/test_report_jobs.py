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


def test_create_report_job_returns_job_id_and_pending_status(client):
    response = client.post("/api/reports", json=make_report_payload())

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "pending"


def test_get_report_job_status_returns_pending_job(client):
    create_response = client.post("/api/reports", json=make_report_payload())
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/reports/{job_id}")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "pending"
    assert data["result_json"] is None
    assert data["error_message"] is None


def test_missing_report_job_returns_404(client):
    response = client.get("/api/reports/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "report job not found"