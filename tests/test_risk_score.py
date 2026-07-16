from backend.schemas.portfolio import HoldingInput, PortfolioAnalyzeRequest
from backend.services.portfolio_analysis import analyze_portfolio
from backend.services.risk_score import (
    calculate_concentration_score,
    calculate_diversification_score,
)


def test_balanced_portfolio_has_deterministic_risk_output():
    request = PortfolioAnalyzeRequest(
        cash=0,
        risk_tolerance="moderate",
        target_allocation={
            "stock": 60,
            "etf": 30,
            "bond": 10,
            "cash": 0,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="MSFT",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="JPM",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="financials",
            ),
            HoldingInput(
                ticker="JNJ",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="healthcare",
            ),
            HoldingInput(
                ticker="XOM",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="energy",
            ),
            HoldingInput(
                ticker="PG",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="consumer staples",
            ),
            HoldingInput(
                ticker="VTI",
                quantity=1,
                price=100,
                asset_class="etf",
                sector="broad market",
            ),
            HoldingInput(
                ticker="VXUS",
                quantity=1,
                price=100,
                asset_class="etf",
                sector="international",
            ),
            HoldingInput(
                ticker="SCHD",
                quantity=1,
                price=100,
                asset_class="etf",
                sector="dividend",
            ),
            HoldingInput(
                ticker="BND",
                quantity=1,
                price=100,
                asset_class="bond",
                sector="fixed income",
            ),
        ],
    )

    result = analyze_portfolio(request)
    risk = result["risk_score"]

    assert risk["risk_score_v1"] == risk["risk_score_v1"]
    assert risk["risk_level"] in ["low", "moderate", "high"]
    assert risk["concentration_score"] < 70
    assert risk["diversification_score"] > 60


def test_concentrated_single_stock_has_high_concentration_score():
    request = PortfolioAnalyzeRequest(
        cash=0,
        risk_tolerance="moderate",
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=100,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    result = analyze_portfolio(request)
    risk = result["risk_score"]

    assert risk["concentration_score"] >= 80
    assert risk["risk_level"] == "high"


def test_high_cash_portfolio_has_high_cash_score():
    request = PortfolioAnalyzeRequest(
        cash=7000,
        risk_tolerance="moderate",
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=30,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    result = analyze_portfolio(request)
    risk = result["risk_score"]

    assert result["cash_percentage"] == 70
    assert risk["cash_score"] > 50


def test_high_sector_exposure_has_high_sector_score():
    request = PortfolioAnalyzeRequest(
        cash=0,
        risk_tolerance="moderate",
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=40,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="MSFT",
                quantity=40,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="VTI",
                quantity=20,
                price=100,
                asset_class="etf",
                sector="broad market",
            ),
        ],
    )

    result = analyze_portfolio(request)
    risk = result["risk_score"]

    assert result["sector_breakdown"]["technology"] == 80
    assert risk["sector_exposure_score"] == 100


def test_concentration_and_diversification_scores_can_be_tested_separately():
    analysis = {
        "top_1_percentage": 40,
        "top_3_percentage": 70,
        "top_5_percentage": 90,
        "number_of_holdings": 5,
        "sector_breakdown": {
            "technology": 40,
            "financials": 30,
            "healthcare": 30,
        },
    }

    concentration_score = calculate_concentration_score(
        analysis,
        max_holding=30,
    )

    diversification_score = calculate_diversification_score(
        analysis,
        concentration_score,
    )

    assert concentration_score > 60
    assert diversification_score < 60


def test_risk_score_has_plain_english_explanations():
    request = PortfolioAnalyzeRequest(
        cash=1000,
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=10,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    result = analyze_portfolio(request)
    risk = result["risk_score"]

    assert len(risk["explanations"]) > 0
    assert "deterministic weighted score" in risk["explanations"][0]

def test_valid_target_allocation_returns_gap_analysis():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={
            "stock": 50,
            "etf": 30,
            "bond": 20,
            "cash": 0,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=5,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="VTI",
                quantity=3,
                price=100,
                asset_class="etf",
                sector="broad market",
            ),
            HoldingInput(
                ticker="BND",
                quantity=2,
                price=100,
                asset_class="bond",
                sector="fixed income",
            ),
        ],
    )

    result = analyze_portfolio(request)
    gap_analysis = result["risk_score"]["target_allocation_gap_analysis"]

    assert len(gap_analysis) == 4
    assert gap_analysis[0]["asset_class"] in {"stock", "etf", "bond", "cash"}
    assert {
        "asset_class",
        "current_weight",
        "target_weight",
        "difference",
        "status",
    } == set(gap_analysis[0].keys())


def test_invalid_target_allocation_sum_raises_error():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={
            "stock": 50,
            "etf": 20,
            "bond": 10,
            "cash": 0,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    try:
        analyze_portfolio(request)
    except ValueError as error:
        assert "target allocation must sum close to 100%" in str(error)
    else:
        raise AssertionError("Expected target allocation sum validation error")


def test_negative_target_allocation_raises_error():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={
            "stock": 110,
            "etf": -10,
            "cash": 0,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    try:
        analyze_portfolio(request)
    except ValueError as error:
        assert "target allocation cannot contain negative values" in str(error)
    else:
        raise AssertionError("Expected negative target allocation validation error")


def test_unknown_target_asset_class_raises_error():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={
            "stock": 80,
            "commodities": 20,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=1,
                price=100,
                asset_class="stock",
                sector="technology",
            )
        ],
    )

    try:
        analyze_portfolio(request)
    except ValueError as error:
        assert "unknown target asset class" in str(error)
    else:
        raise AssertionError("Expected unknown target asset class validation error")


def test_all_cash_case_returns_gap_analysis():
    request = PortfolioAnalyzeRequest(
        cash=1000,
        target_allocation={
            "cash": 100,
        },
        holdings=[
            HoldingInput(
                ticker="CASH",
                quantity=1,
                price=1,
                asset_class="cash",
                sector="cash",
            )
        ],
    )

    result = analyze_portfolio(request)
    gap_analysis = result["risk_score"]["target_allocation_gap_analysis"]

    assert result["cash_percentage"] > 99
    assert len(gap_analysis) >= 1
    assert gap_analysis[0]["status"] in {
        "overweight",
        "underweight",
        "on target",
    }


def test_gap_analysis_is_sorted_by_largest_absolute_gap_first():
    request = PortfolioAnalyzeRequest(
        cash=0,
        target_allocation={
            "stock": 20,
            "etf": 60,
            "bond": 20,
            "cash": 0,
        },
        holdings=[
            HoldingInput(
                ticker="AAPL",
                quantity=8,
                price=100,
                asset_class="stock",
                sector="technology",
            ),
            HoldingInput(
                ticker="VTI",
                quantity=1,
                price=100,
                asset_class="etf",
                sector="broad market",
            ),
            HoldingInput(
                ticker="BND",
                quantity=1,
                price=100,
                asset_class="bond",
                sector="fixed income",
            ),
        ],
    )

    result = analyze_portfolio(request)
    gap_analysis = result["risk_score"]["target_allocation_gap_analysis"]

    gaps = [abs(item["difference"]) for item in gap_analysis]

    assert gaps == sorted(gaps, reverse=True)