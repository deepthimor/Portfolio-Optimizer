import pytest
from pydantic import ValidationError

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


def test_analyze_portfolio_calculates_asset_class_breakdown():
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
                "ticker": "VTI",
                "quantity": 5,
                "price": 100,
                "asset_class": "etf",
                "sector": "broad market",
            },
        ],
    )

    result = analyze_portfolio(request)

    assert result["asset_class_breakdown"]["stock"] == 50
    assert result["asset_class_breakdown"]["etf"] == 50


def test_analyze_portfolio_all_cash_with_placeholder_cash_holding():
    request = PortfolioAnalyzeRequest(
        cash=1000,
        holdings=[
            {
                "ticker": "CASH",
                "quantity": 1,
                "price": 0.01,
                "asset_class": "cash",
                "sector": "cash",
            }
        ],
    )

    result = analyze_portfolio(request)

    assert result["total_portfolio_value"] == 1000.01
    assert result["cash"] == 1000
    assert result["cash_percentage"] == 100


def test_analyze_portfolio_allows_duplicate_tickers_as_separate_rows():
    request = PortfolioAnalyzeRequest(
        cash=0,
        holdings=[
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
    )

    result = analyze_portfolio(request)

    assert len(result["holdings"]) == 2
    assert result["total_holdings_value"] == 300
    assert result["sector_breakdown"]["technology"] == 100


def test_analyze_portfolio_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(
            cash=0,
            holdings=[
                {
                    "ticker": "AAPL",
                    "quantity": 0,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        )


def test_analyze_portfolio_rejects_negative_price():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(
            cash=0,
            holdings=[
                {
                    "ticker": "AAPL",
                    "quantity": 1,
                    "price": -100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        )


def test_analyze_portfolio_rejects_missing_ticker():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(
            cash=0,
            holdings=[
                {
                    "ticker": "",
                    "quantity": 1,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        )


def test_analyze_portfolio_rejects_missing_sector():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(
            cash=0,
            holdings=[
                {
                    "ticker": "AAPL",
                    "quantity": 1,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "",
                }
            ],
        )


def test_analyze_portfolio_rejects_empty_portfolio():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(cash=1000, holdings=[])


def test_analyze_portfolio_rejects_negative_quantity():
    with pytest.raises(ValidationError):
        PortfolioAnalyzeRequest(
            cash=0,
            holdings=[
                {
                    "ticker": "AAPL",
                    "quantity": -1,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        )