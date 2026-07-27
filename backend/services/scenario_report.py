"""Deterministic scenario report calculations.

These calculations are simple stress-test estimates. They are not forecasts,
do not use live market data, and do not recommend buying or selling securities.
"""

from backend.schemas.portfolio import ReportRequest

DISCLAIMER = "Educational information only; scenario reports are not forecasts."

SUPPORTED_SCENARIOS = [
    "market_down_25",
    "tech_down_40",
    "rates_up",
    "cash_return",
    "international_underperformance",
    "concentrated_holding_drop",
]

SCENARIO_ASSUMPTIONS = {
    "market_down_25": [
        "Non-cash holdings decline by 25%.",
        "Cash is unchanged.",
    ],
    "tech_down_40": [
        "Technology holdings decline by 40%.",
        "Other holdings are unchanged.",
        "Cash is unchanged.",
    ],
    "rates_up": [
        "Bond and fixed income holdings decline by 10%.",
        "Other holdings are unchanged.",
        "Cash is unchanged.",
    ],
    "cash_return": [
        "Cash earns 4%.",
        "Holdings are unchanged.",
    ],
    "international_underperformance": [
        "International and emerging market holdings decline by 20%.",
        "Other holdings are unchanged.",
        "Cash is unchanged.",
    ],
    "concentrated_holding_drop": [
        "The largest holding declines by 30%.",
        "Other holdings are unchanged.",
        "Cash is unchanged.",
    ],
}


def round_value(value: float) -> float:
    return round(value, 2)


def holding_value(holding) -> float:
    return holding.quantity * holding.price


def is_cash_holding(holding) -> bool:
    return (
        holding.asset_class.lower().strip() == "cash"
        or holding.ticker.upper().strip() == "CASH"
    )


def is_technology_holding(holding) -> bool:
    return holding.sector.lower().strip() in {"technology", "tech"}


def is_fixed_income_holding(holding) -> bool:
    asset_class = holding.asset_class.lower().strip()
    sector = holding.sector.lower().strip()

    return asset_class in {"bond", "bonds", "fixed income"} or sector == "fixed income"


def is_international_holding(holding) -> bool:
    text = f"{holding.asset_class} {holding.sector}".lower()

    international_terms = [
        "international",
        "foreign",
        "non-us",
        "non us",
        "developed international",
        "emerging",
        "emerging markets",
    ]

    return any(term in text for term in international_terms)


def get_largest_holding_ticker(request: ReportRequest) -> str:
    largest_holding = max(request.holdings, key=holding_value)
    return largest_holding.ticker.upper().strip()


def get_holding_shock(
    scenario_name: str,
    holding,
    largest_holding_ticker: str,
) -> tuple[float, str]:
    if is_cash_holding(holding):
        return 0.0, "Cash holding is unchanged in this scenario."

    if scenario_name == "market_down_25":
        return -0.25, "Non-cash holding receives -25% market scenario shock."

    if scenario_name == "tech_down_40" and is_technology_holding(holding):
        return -0.40, "Technology holding receives -40% technology scenario shock."

    if scenario_name == "rates_up" and is_fixed_income_holding(holding):
        return -0.10, "Bond or fixed income holding receives -10% rates-up shock."

    if scenario_name == "international_underperformance" and is_international_holding(holding):
        return -0.20, "International holding receives -20% underperformance shock."

    if (
        scenario_name == "concentrated_holding_drop"
        and holding.ticker.upper().strip() == largest_holding_ticker
    ):
        return -0.30, "Largest holding receives -30% concentration shock."

    return 0.0, "Holding is unchanged in this scenario."


def get_cash_shock(scenario_name: str) -> float:
    if scenario_name == "cash_return":
        return 0.04

    return 0.0


def validate_scenarios(scenarios: list[str]) -> None:
    unknown_scenarios = [
        scenario for scenario in scenarios if scenario not in SUPPORTED_SCENARIOS
    ]

    if unknown_scenarios:
        raise ValueError(f"unknown scenario name: {unknown_scenarios[0]}")


def calculate_starting_value(request: ReportRequest) -> float:
    holdings_value = sum(holding_value(holding) for holding in request.holdings)
    return round_value(holdings_value + request.cash)


def calculate_scenario_result(request: ReportRequest, scenario_name: str) -> dict:
    starting_value = calculate_starting_value(request)
    largest_holding_ticker = get_largest_holding_ticker(request)

    scenario_holdings_value = 0.0
    impacts = []

    for holding in request.holdings:
        start_value = holding_value(holding)
        shock, assumption = get_holding_shock(
            scenario_name,
            holding,
            largest_holding_ticker,
        )
        scenario_value = start_value * (1 + shock)
        dollar_change = scenario_value - start_value

        scenario_holdings_value += scenario_value

        if dollar_change != 0:
            impacts.append(
                {
                    "ticker": holding.ticker.upper().strip(),
                    "starting_value": round_value(start_value),
                    "scenario_value": round_value(scenario_value),
                    "dollar_change": round_value(dollar_change),
                    "percent_change": round_value(shock * 100),
                    "applied_assumption": assumption,
                }
            )

    scenario_cash_value = request.cash * (1 + get_cash_shock(scenario_name))
    scenario_value = round_value(scenario_holdings_value + scenario_cash_value)
    dollar_change = round_value(scenario_value - starting_value)

    percent_change = 0.0
    if starting_value > 0:
        percent_change = round_value((dollar_change / starting_value) * 100)

    most_impacted_holdings = sorted(
        impacts,
        key=lambda impact: abs(impact["dollar_change"]),
        reverse=True,
    )[:5]

    return {
        "scenario_name": scenario_name,
        "starting_value": starting_value,
        "scenario_value": scenario_value,
        "dollar_change": dollar_change,
        "percent_change": percent_change,
        "most_impacted_holdings": most_impacted_holdings,
        "assumptions": SCENARIO_ASSUMPTIONS[scenario_name],
    }


def build_scenario_report(request: ReportRequest) -> dict:
    scenarios = request.scenarios or SUPPORTED_SCENARIOS

    validate_scenarios(scenarios)

    starting_value = calculate_starting_value(request)

    return {
        "starting_value": starting_value,
        "results": [
            calculate_scenario_result(request, scenario)
            for scenario in scenarios
        ],
        "disclaimer": DISCLAIMER,
    }