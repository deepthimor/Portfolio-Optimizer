from backend.schemas.portfolio import PortfolioAnalyzeRequest
from backend.services.portfolio_analysis import analyze_portfolio


def test_analyze_portfolio_calculates_total_value():
    request = PortfolioAnalyzeRequest(
        cash=500,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 5,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            }
        ],
    )

    result = analyze_portfolio(request)

    assert result["total_portfolio_value"] == 1000
    assert result["total_holdings_value"] == 500
    assert result["cash_percentage"] == 50


def test_analyze_portfolio_calculates_weights():
    request = PortfolioAnalyzeRequest(
        cash=0,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 5,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "MSFT",
                "quantity": 5,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
        ],
    )

    result = analyze_portfolio(request)

    assert result["holdings"][0]["weight"] == 50
    assert result["holdings"][1]["weight"] == 50


def test_analyze_portfolio_calculates_sector_breakdown():
    request = PortfolioAnalyzeRequest(
        cash=0,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 5,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "JPM",
                "quantity": 5,
                "price": 100,
                "asset_class": "stock",
                "sector": "financials",
            },
        ],
    )

    result = analyze_portfolio(request)

    assert result["sector_breakdown"]["technology"] == 50
    assert result["sector_breakdown"]["financials"] == 50