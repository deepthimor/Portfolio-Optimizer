from backend.schemas.portfolio import PortfolioAnalyzeRequest
from backend.services.portfolio_analysis import analyze_portfolio


def test_single_overweight_stock_creates_trim_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=30,
        max_sector=100,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 70,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "VTI",
                "quantity": 30,
                "price": 1,
                "asset_class": "etf",
                "sector": "broad market",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    assert recommendations[0]["reason_code"] == "OVERWEIGHT_HOLDING"
    assert recommendations[0]["ticker"] == "AAPL"
    assert recommendations[0]["before_weight"] == 70
    assert recommendations[0]["after_weight_estimate"] == 30
    assert recommendations[0]["amount_or_percent"] == 40


def test_two_overweight_stocks_are_sorted_by_overweight_amount():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=20,
        max_sector=100,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 50,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "MSFT",
                "quantity": 30,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "VTI",
                "quantity": 20,
                "price": 1,
                "asset_class": "etf",
                "sector": "broad market",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    holding_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation["reason_code"] == "OVERWEIGHT_HOLDING"
    ]

    assert holding_recommendations[0]["ticker"] == "AAPL"
    assert holding_recommendations[0]["amount_or_percent"] == 30
    assert holding_recommendations[1]["ticker"] == "MSFT"
    assert holding_recommendations[1]["amount_or_percent"] == 10


def test_overweight_sector_with_multiple_holdings_creates_sector_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=100,
        max_sector=50,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 40,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "MSFT",
                "quantity": 30,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "JPM",
                "quantity": 30,
                "price": 1,
                "asset_class": "stock",
                "sector": "financials",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    sector_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation["reason_code"] == "OVERWEIGHT_SECTOR"
    ]

    assert len(sector_recommendations) == 1
    assert sector_recommendations[0]["amount_or_percent"] == 20
    assert "technology" in sector_recommendations[0]["human_reason"]


def test_no_overweight_holdings_returns_balanced_no_action():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=60,
        max_sector=80,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 40,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "VTI",
                "quantity": 40,
                "price": 1,
                "asset_class": "etf",
                "sector": "broad market",
            },
            {
                "ticker": "BND",
                "quantity": 20,
                "price": 1,
                "asset_class": "bond",
                "sector": "fixed income",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    assert len(recommendations) == 1
    assert recommendations[0]["reason_code"] == "BALANCED_NO_ACTION"
    assert recommendations[0]["action"] == "no_action"


def test_cash_does_not_create_overweight_holding_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=90,
        max_holding=20,
        max_sector=20,
        holdings=[
            {
                "ticker": "CASH",
                "quantity": 10,
                "price": 1,
                "asset_class": "cash",
                "sector": "cash",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    assert all(
        recommendation["reason_code"] != "OVERWEIGHT_HOLDING"
        for recommendation in recommendations
    )