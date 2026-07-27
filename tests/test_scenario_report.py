import pytest

from backend.schemas.portfolio import ReportRequest
from backend.services.scenario_report import build_scenario_report


def make_request(scenarios=None):
    return ReportRequest(
        cash=1000,
        scenarios=scenarios,
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 10,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "VXUS",
                "quantity": 10,
                "price": 50,
                "asset_class": "international",
                "sector": "international equity",
            },
            {
                "ticker": "BND",
                "quantity": 10,
                "price": 80,
                "asset_class": "bond",
                "sector": "fixed income",
            },
        ],
    )


def get_result(report, scenario_name):
    return next(
        result for result in report["results"]
        if result["scenario_name"] == scenario_name
    )


def test_market_down_25_scenario():
    report = build_scenario_report(make_request(["market_down_25"]))
    result = get_result(report, "market_down_25")

    assert result["starting_value"] == 3300
    assert result["scenario_value"] == 2725
    assert result["dollar_change"] == -575
    assert result["percent_change"] == -17.42
    assert result["assumptions"]


def test_tech_down_40_scenario():
    report = build_scenario_report(make_request(["tech_down_40"]))
    result = get_result(report, "tech_down_40")

    assert result["scenario_value"] == 2900
    assert result["dollar_change"] == -400
    assert result["most_impacted_holdings"][0]["ticker"] == "AAPL"


def test_rates_up_scenario():
    report = build_scenario_report(make_request(["rates_up"]))
    result = get_result(report, "rates_up")

    assert result["scenario_value"] == 3220
    assert result["dollar_change"] == -80
    assert result["most_impacted_holdings"][0]["ticker"] == "BND"


def test_cash_return_scenario():
    report = build_scenario_report(make_request(["cash_return"]))
    result = get_result(report, "cash_return")

    assert result["scenario_value"] == 3340
    assert result["dollar_change"] == 40
    assert result["percent_change"] == 1.21


def test_international_underperformance_scenario():
    report = build_scenario_report(make_request(["international_underperformance"]))
    result = get_result(report, "international_underperformance")

    assert result["scenario_value"] == 3200
    assert result["dollar_change"] == -100
    assert result["most_impacted_holdings"][0]["ticker"] == "VXUS"


def test_concentrated_holding_drop_scenario():
    report = build_scenario_report(make_request(["concentrated_holding_drop"]))
    result = get_result(report, "concentrated_holding_drop")

    assert result["scenario_value"] == 3000
    assert result["dollar_change"] == -300
    assert result["most_impacted_holdings"][0]["ticker"] == "AAPL"


def test_default_report_runs_all_scenarios():
    report = build_scenario_report(make_request())

    assert len(report["results"]) == 6
    assert report["starting_value"] == 3300
    assert "not forecasts" in report["disclaimer"]


def test_unknown_scenario_is_rejected():
    request = make_request(["made_up_scenario"])

    with pytest.raises(ValueError, match="unknown scenario name"):
        build_scenario_report(request)


def test_report_output_shape_includes_required_fields():
    report = build_scenario_report(make_request(["market_down_25"]))
    result = report["results"][0]

    assert set(result.keys()) == {
        "scenario_name",
        "starting_value",
        "scenario_value",
        "dollar_change",
        "percent_change",
        "most_impacted_holdings",
        "assumptions",
    }