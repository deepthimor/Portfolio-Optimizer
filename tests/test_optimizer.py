import pytest

from backend.schemas.portfolio import PortfolioAnalyzeRequest
from backend.services.portfolio_analysis import analyze_portfolio


def test_single_overweight_stock_creates_trim_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=30,
        max_sector=100,
        target_allocation={"stock": 70, "etf": 30, "cash": 0},
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
        target_allocation={"stock": 80, "etf": 20, "cash": 0},
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
        target_allocation={"stock": 100, "cash": 0},
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


def test_balanced_portfolio_returns_no_major_action():
    request = PortfolioAnalyzeRequest(
        cash=10,
        max_holding=60,
        max_sector=80,
        risk_tolerance="moderate",
        target_allocation={"stock": 40, "etf": 40, "bond": 10, "cash": 10},
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
                "quantity": 10,
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
        target_allocation={"cash": 100},
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


def test_underweight_bonds_create_add_exposure_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=20,
        max_holding=80,
        max_sector=90,
        risk_tolerance="moderate",
        target_allocation={"stock": 50, "bond": 30, "cash": 20},
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 80,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    bond_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation["reason_code"] == "UNDERWEIGHT_ASSET_CLASS"
        and "bond" in recommendation["human_reason"]
    ]

    assert len(bond_recommendations) == 1
    assert bond_recommendations[0]["action"] == "add_exposure"
    assert bond_recommendations[0]["amount_or_percent"] == 30


def test_underweight_equities_create_add_exposure_recommendation():
    request = PortfolioAnalyzeRequest(
        cash=20,
        max_holding=90,
        max_sector=90,
        risk_tolerance="moderate",
        target_allocation={"stock": 60, "bond": 20, "cash": 20},
        holdings=[
            {
                "ticker": "BND",
                "quantity": 80,
                "price": 1,
                "asset_class": "bond",
                "sector": "fixed income",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    stock_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation["reason_code"] == "UNDERWEIGHT_ASSET_CLASS"
        and "stock" in recommendation["human_reason"]
    ]

    assert len(stock_recommendations) == 1
    assert stock_recommendations[0]["action"] == "add_exposure"
    assert stock_recommendations[0]["amount_or_percent"] == 60


def test_buy_recommendations_respect_cash_requirement():
    request = PortfolioAnalyzeRequest(
        cash=0,
        max_holding=90,
        max_sector=90,
        risk_tolerance="moderate",
        target_allocation={"stock": 60, "bond": 30, "cash": 10},
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 100,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    )

    result = analyze_portfolio(request)
    recommendations = result["optimizer"]["recommendations"]

    assert any(
        recommendation["reason_code"] == "BELOW_CASH_TARGET"
        for recommendation in recommendations
    )

    assert all(
        recommendation["reason_code"] != "UNDERWEIGHT_ASSET_CLASS"
        for recommendation in recommendations
    )


def test_invalid_target_allocation_is_rejected():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={"stock": 70, "bond": 70},
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 1,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    )

    with pytest.raises(ValueError):
        analyze_portfolio(request)


def test_tiny_portfolio_still_returns_structured_recommendations():
    request = PortfolioAnalyzeRequest(
        cash=1,
        max_holding=90,
        max_sector=90,
        risk_tolerance="aggressive",
        target_allocation={"stock": 50, "cash": 50},
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 1,
                "price": 1,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    )

    result = analyze_portfolio(request)
    optimizer = result["optimizer"]

    assert "recommendations" in optimizer
    assert "disclaimer" in optimizer
    assert len(optimizer["recommendations"]) >= 1