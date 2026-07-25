def make_holding(
    ticker: str,
    quantity: float,
    price: float,
    asset_class: str,
    sector: str,
) -> dict:
    return {
        "ticker": ticker,
        "quantity": quantity,
        "price": price,
        "asset_class": asset_class,
        "sector": sector,
    }


OVERWEIGHT_STOCK_PORTFOLIO = {
    "cash": 0,
    "max_holding": 30,
    "max_sector": 100,
    "target_allocation": {"stock": 70, "etf": 30, "cash": 0},
    "holdings": [
        make_holding("AAPL", 70, 1, "stock", "technology"),
        make_holding("VTI", 30, 1, "etf", "broad market"),
    ],
}


OVERWEIGHT_SECTOR_PORTFOLIO = {
    "cash": 0,
    "max_holding": 100,
    "max_sector": 50,
    "target_allocation": {"stock": 100, "cash": 0},
    "holdings": [
        make_holding("AAPL", 40, 1, "stock", "technology"),
        make_holding("MSFT", 30, 1, "stock", "technology"),
        make_holding("JPM", 30, 1, "stock", "financials"),
    ],
}


BALANCED_PORTFOLIO = {
    "cash": 10,
    "max_holding": 60,
    "max_sector": 80,
    "risk_tolerance": "moderate",
    "target_allocation": {"stock": 40, "etf": 40, "bond": 10, "cash": 10},
    "holdings": [
        make_holding("AAPL", 40, 1, "stock", "technology"),
        make_holding("VTI", 40, 1, "etf", "broad market"),
        make_holding("BND", 10, 1, "bond", "fixed income"),
    ],
}


ALL_CASH_PORTFOLIO = {
    "cash": 90,
    "max_holding": 20,
    "max_sector": 20,
    "target_allocation": {"cash": 100},
    "holdings": [
        make_holding("CASH", 10, 1, "cash", "cash"),
    ],
}


UNDERWEIGHT_BONDS_PORTFOLIO = {
    "cash": 20,
    "max_holding": 80,
    "max_sector": 90,
    "risk_tolerance": "moderate",
    "target_allocation": {"stock": 50, "bond": 30, "cash": 20},
    "holdings": [
        make_holding("AAPL", 80, 1, "stock", "technology"),
    ],
}


TINY_PORTFOLIO = {
    "cash": 1,
    "max_holding": 90,
    "max_sector": 90,
    "risk_tolerance": "aggressive",
    "target_allocation": {"stock": 50, "cash": 50},
    "holdings": [
        make_holding("AAPL", 1, 1, "stock", "technology"),
    ],
}