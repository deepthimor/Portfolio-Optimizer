from fastapi.testclient import TestClient

from backend.api.main import app
from tests.fixtures.optimizer_cases import OVERWEIGHT_STOCK_PORTFOLIO


client = TestClient(app)


def test_analyze_endpoint_returns_optimizer_output():
    response = client.post("/api/portfolio/analyze", json=OVERWEIGHT_STOCK_PORTFOLIO)

    assert response.status_code == 200

    payload = response.json()

    assert "optimizer" in payload
    assert "recommendations" in payload["optimizer"]
    assert "disclaimer" in payload["optimizer"]
    assert payload["optimizer"]["recommendations"][0]["reason_code"] == "OVERWEIGHT_HOLDING"