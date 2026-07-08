def test_analyze_portfolio_success(client, valid_portfolio_payload):
    response = client.post("/api/portfolio/analyze", json=valid_portfolio_payload)

    assert response.status_code == 200

    data = response.json()

    assert data["cash"] == 2500
    assert data["total_holdings_value"] == 3275
    assert data["total_portfolio_value"] == 5775
    assert len(data["holdings"]) == 2
    assert data["holdings"][0]["ticker"] == "AAPL"


def test_analyze_rejects_missing_ticker(client, invalid_portfolio_payloads):
    response = client.post(
        "/api/portfolio/analyze",
        json=invalid_portfolio_payloads["missing_ticker"],
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_analyze_rejects_empty_portfolio(client, invalid_portfolio_payloads):
    response = client.post(
        "/api/portfolio/analyze",
        json=invalid_portfolio_payloads["empty_portfolio"],
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_analyze_rejects_invalid_numbers(client, invalid_portfolio_payloads):
    for payload_name in ["negative_cash", "zero_quantity", "negative_price"]:
        response = client.post(
            "/api/portfolio/analyze",
            json=invalid_portfolio_payloads[payload_name],
        )

        assert response.status_code == 422
        assert "detail" in response.json()


def test_analyze_allows_duplicate_tickers_as_separate_rows(
    client,
    valid_portfolio_payload,
):
    payload = {
        "cash": 0,
        "holdings": [
            {
                "ticker": "AAPL",
                "quantity": 1,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "AAPL",
                "quantity": 2,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    }

    response = client.post("/api/portfolio/analyze", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert len(data["holdings"]) == 2
    assert data["total_portfolio_value"] == 300