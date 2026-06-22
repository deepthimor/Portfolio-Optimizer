from collections import defaultdict
from backend.schemas.portfolio import PortfolioAnalyzeRequest


def round_value(value: float) -> float:
    return round(value, 2)


def analyze_portfolio(request: PortfolioAnalyzeRequest) -> dict:
    holdings_value = sum(
        holding.quantity * holding.price for holding in request.holdings
    )
    total_value = holdings_value + request.cash

    if total_value <= 0:
        raise ValueError("portfolio value must be greater than zero")

    analyzed_holdings = []
    sector_totals = defaultdict(float)
    asset_class_totals = defaultdict(float)

    for holding in request.holdings:
        ticker = holding.ticker.upper().strip()
        asset_class = holding.asset_class.lower().strip()
        sector = holding.sector.lower().strip()
        market_value = holding.quantity * holding.price
        weight = (market_value / total_value) * 100

        analyzed_holding = {
            "ticker": ticker,
            "quantity": holding.quantity,
            "price": round_value(holding.price),
            "market_value": round_value(market_value),
            "weight": round_value(weight),
            "asset_class": asset_class,
            "sector": sector,
        }

        analyzed_holdings.append(analyzed_holding)
        sector_totals[sector] += market_value
        asset_class_totals[asset_class] += market_value

    analyzed_holdings.sort(key=lambda item: item["market_value"], reverse=True)

    top_holdings = [
        {
            "ticker": holding["ticker"],
            "market_value": holding["market_value"],
            "weight": holding["weight"],
        }
        for holding in analyzed_holdings[:5]
    ]

    sector_breakdown = {
        sector: round_value((value / total_value) * 100)
        for sector, value in sector_totals.items()
    }

    asset_class_breakdown = {
        asset_class: round_value((value / total_value) * 100)
        for asset_class, value in asset_class_totals.items()
    }

    return {
        "total_portfolio_value": round_value(total_value),
        "total_holdings_value": round_value(holdings_value),
        "cash": round_value(request.cash),
        "cash_percentage": round_value((request.cash / total_value) * 100),
        "holdings": analyzed_holdings,
        "top_holdings": top_holdings,
        "sector_breakdown": sector_breakdown,
        "asset_class_breakdown": asset_class_breakdown,
    }