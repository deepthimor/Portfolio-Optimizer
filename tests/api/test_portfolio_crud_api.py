def test_create_list_and_get_saved_portfolio(client, saved_portfolio_payload):
    create_response = client.post(
        "/api/portfolio",
        json=saved_portfolio_payload,
    )

    assert create_response.status_code == 200

    created = create_response.json()

    assert created["id"] == 1
    assert created["name"] == "Test Portfolio"
    assert created["cash"] == 2500

    list_response = client.get("/api/portfolio")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/api/portfolio/{created['id']}")

    assert get_response.status_code == 200

    portfolio = get_response.json()

    assert portfolio["id"] == created["id"]
    assert portfolio["name"] == "Test Portfolio"
    assert len(portfolio["holdings"]) == 2


def test_update_saved_portfolio_metadata(client, saved_portfolio_payload):
    create_response = client.post(
        "/api/portfolio",
        json=saved_portfolio_payload,
    )

    portfolio_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/portfolio/{portfolio_id}",
        json={
            "name": "Updated Portfolio",
            "cash": 5000,
        },
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["name"] == "Updated Portfolio"
    assert updated["cash"] == 5000


def test_delete_portfolio_with_holdings(client, saved_portfolio_payload):
    create_response = client.post(
        "/api/portfolio",
        json=saved_portfolio_payload,
    )

    portfolio_id = create_response.json()["id"]

    before_delete = client.get(f"/api/portfolio/{portfolio_id}")

    assert before_delete.status_code == 200
    assert len(before_delete.json()["holdings"]) == 2

    delete_response = client.delete(f"/api/portfolio/{portfolio_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "portfolio deleted"}

    after_delete = client.get(f"/api/portfolio/{portfolio_id}")

    assert after_delete.status_code == 404
    assert after_delete.json() == {"detail": "portfolio not found"}


def test_invalid_portfolio_id_returns_clean_404(client):
    response = client.get("/api/portfolio/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "portfolio not found"}


def test_add_update_and_delete_holding(client, saved_portfolio_payload):
    create_response = client.post(
        "/api/portfolio",
        json=saved_portfolio_payload,
    )

    portfolio_id = create_response.json()["id"]

    add_response = client.post(
        f"/api/portfolio/{portfolio_id}/holdings",
        json={
            "ticker": "JPM",
            "quantity": 4,
            "price": 205,
            "asset_class": "stock",
            "sector": "financials",
        },
    )

    assert add_response.status_code == 201

    holding = add_response.json()

    assert holding["ticker"] == "JPM"
    assert holding["portfolio_id"] == portfolio_id

    update_response = client.patch(
        f"/api/portfolio/holdings/{holding['id']}",
        json={
            "quantity": 5,
            "price": 210,
        },
    )

    assert update_response.status_code == 200

    updated_holding = update_response.json()

    assert updated_holding["quantity"] == 5
    assert updated_holding["price"] == 210

    delete_response = client.delete(
        f"/api/portfolio/holdings/{holding['id']}",
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "holding deleted"}


def test_invalid_holding_id_returns_clean_404(client):
    patch_response = client.patch(
        "/api/portfolio/holdings/999999",
        json={"quantity": 5},
    )

    assert patch_response.status_code == 404
    assert patch_response.json() == {"detail": "holding not found"}

    delete_response = client.delete("/api/portfolio/holdings/999999")

    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "holding not found"}