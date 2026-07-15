DEFAULT_TARGET_ALLOCATION = {
    "stock": 60.0,
    "etf": 30.0,
    "bond": 10.0,
    "cash": 0.0,
}


RISK_TOLERANCE_SETTINGS = {
    "conservative": {
        "max_holding": 20.0,
        "max_sector": 35.0,
        "cash_threshold": 15.0,
    },
    "moderate": {
        "max_holding": 30.0,
        "max_sector": 45.0,
        "cash_threshold": 25.0,
    },
    "aggressive": {
        "max_holding": 40.0,
        "max_sector": 55.0,
        "cash_threshold": 35.0,
    },
}


def round_score(value: float) -> float:
    return round(max(0, min(100, value)), 2)


def get_risk_settings(request) -> dict:
    risk_tolerance = (getattr(request, "risk_tolerance", None) or "moderate").lower()
    settings = RISK_TOLERANCE_SETTINGS.get(
        risk_tolerance,
        RISK_TOLERANCE_SETTINGS["moderate"],
    )

    max_holding = getattr(request, "max_holding", None) or settings["max_holding"]
    max_sector = getattr(request, "max_sector", None) or settings["max_sector"]
    target_allocation = (
        getattr(request, "target_allocation", None) or DEFAULT_TARGET_ALLOCATION
    )

    return {
        "risk_tolerance": risk_tolerance,
        "max_holding": float(max_holding),
        "max_sector": float(max_sector),
        "cash_threshold": float(settings["cash_threshold"]),
        "target_allocation": {
            key.lower(): float(value) for key, value in target_allocation.items()
        },
        "expected_return": getattr(request, "expected_return", None),
        "volatility": getattr(request, "volatility", None),
    }


def calculate_concentration_score(analysis: dict, max_holding: float) -> float:
    single_holding_score = round_score(
        (analysis["top_1_percentage"] / max_holding) * 100
    )

    top_three_score = round_score(
        (analysis["top_3_percentage"] / (max_holding * 2)) * 100
    )

    top_five_score = round_score(
        (analysis["top_5_percentage"] / (max_holding * 3)) * 100
    )

    return round_score(
        (single_holding_score * 0.50)
        + (top_three_score * 0.30)
        + (top_five_score * 0.20)
    )


def calculate_diversification_score(
    analysis: dict,
    concentration_score: float,
) -> float:
    holding_count_score = round_score(
        (analysis["number_of_holdings"] / 10) * 100
    )

    sector_count_score = round_score(
        (len(analysis["sector_breakdown"]) / 5) * 100
    )

    concentration_inverse = round_score(100 - concentration_score)

    return round_score(
        (holding_count_score * 0.40)
        + (sector_count_score * 0.30)
        + (concentration_inverse * 0.30)
    )


def calculate_sector_exposure_score(analysis: dict, max_sector: float) -> float:
    largest_sector_percentage = max(analysis["sector_breakdown"].values())

    return round_score((largest_sector_percentage / max_sector) * 100)


def calculate_cash_score(analysis: dict, cash_threshold: float) -> float:
    cash_percentage = analysis["cash_percentage"]

    if cash_percentage <= cash_threshold:
        return 0.0

    return round_score(
        ((cash_percentage - cash_threshold) / (100 - cash_threshold)) * 100
    )


def calculate_target_allocation_gap_score(
    analysis: dict,
    target_allocation: dict,
) -> float:
    current_allocation = {
        key.lower(): float(value)
        for key, value in analysis["asset_class_breakdown"].items()
    }
    current_allocation["cash"] = float(analysis["cash_percentage"])

    allocation_keys = set(current_allocation.keys()) | set(target_allocation.keys())

    if not allocation_keys:
        return 0.0

    total_gap = sum(
        abs(current_allocation.get(key, 0.0) - target_allocation.get(key, 0.0))
        for key in allocation_keys
    )

    average_gap = total_gap / len(allocation_keys)

    return round_score(average_gap * 2)


def get_risk_level(risk_score: float) -> str:
    if risk_score <= 33:
        return "low"

    if risk_score <= 66:
        return "moderate"

    return "high"


def build_risk_explanations(risk_result: dict) -> list[str]:
    return [
        (
            "Risk score v1 is a deterministic weighted score using concentration, "
            "sector exposure, cash percentage, and target allocation gaps."
        ),
        (
            f"Concentration score is {risk_result['concentration_score']} and is based on "
            "top 1, top 3, and top 5 holding exposure."
        ),
        (
            f"Diversification score is {risk_result['diversification_score']} and is based on "
            "number of holdings, number of sectors, and concentration."
        ),
        (
            f"Sector exposure score is {risk_result['sector_exposure_score']} and compares "
            "the largest sector to the max sector threshold."
        ),
        (
            f"Cash score is {risk_result['cash_score']} and measures cash above the selected "
            "risk tolerance threshold."
        ),
        (
            f"Target allocation gap score is {risk_result['target_allocation_gap_score']} and "
            "compares current allocation to target allocation."
        ),
    ]


def calculate_risk_score(analysis: dict, request) -> dict:
    settings = get_risk_settings(request)

    concentration_score = calculate_concentration_score(
        analysis,
        settings["max_holding"],
    )

    diversification_score = calculate_diversification_score(
        analysis,
        concentration_score,
    )

    sector_exposure_score = calculate_sector_exposure_score(
        analysis,
        settings["max_sector"],
    )

    cash_score = calculate_cash_score(
        analysis,
        settings["cash_threshold"],
    )

    target_allocation_gap_score = calculate_target_allocation_gap_score(
        analysis,
        settings["target_allocation"],
    )

    risk_score_v1 = round_score(
        (concentration_score * 0.35)
        + (sector_exposure_score * 0.25)
        + (cash_score * 0.20)
        + (target_allocation_gap_score * 0.20)
    )

    risk_result = {
        "risk_score_v1": risk_score_v1,
        "risk_level": get_risk_level(risk_score_v1),
        "concentration_score": concentration_score,
        "diversification_score": diversification_score,
        "sector_exposure_score": sector_exposure_score,
        "cash_score": cash_score,
        "target_allocation_gap_score": target_allocation_gap_score,
        "inputs": settings,
    }

    risk_result["explanations"] = build_risk_explanations(risk_result)

    return risk_result