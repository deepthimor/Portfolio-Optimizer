DISCLAIMER = "Educational information only; not financial advice."

REASON_CODES = {
    "OVERWEIGHT_HOLDING",
    "OVERWEIGHT_SECTOR",
    "BELOW_CASH_TARGET",
    "UNDERWEIGHT_ASSET_CLASS",
    "BALANCED_NO_ACTION",
}

CASH_REQUIREMENTS = {
    "conservative": 15.0,
    "moderate": 10.0,
    "aggressive": 5.0,
}


def round_value(value: float) -> float:
    return round(value, 2)


def get_priority(amount: float) -> str:
    if amount >= 15:
        return "high"
    if amount >= 5:
        return "medium"
    return "low"


def get_cash_requirement(analysis: dict) -> float:
    risk_tolerance = analysis["risk_score"]["inputs"].get("risk_tolerance", "moderate")
    return CASH_REQUIREMENTS.get(risk_tolerance, CASH_REQUIREMENTS["moderate"])


def build_overweight_holding_recommendations(analysis: dict) -> list[dict]:
    risk_inputs = analysis["risk_score"]["inputs"]
    max_holding = risk_inputs["max_holding"]

    recommendations = []

    for holding in analysis["holdings"]:
        if holding["asset_class"] == "cash":
            continue

        before_weight = holding["weight"]

        if before_weight > max_holding:
            overweight_amount = round_value(before_weight - max_holding)

            recommendations.append(
                {
                    "action": "reduce_exposure",
                    "ticker": holding["ticker"],
                    "amount_or_percent": overweight_amount,
                    "reason_code": "OVERWEIGHT_HOLDING",
                    "human_reason": (
                        f"{holding['ticker']} is {before_weight}% of the portfolio, "
                        f"which is above the max holding threshold of {max_holding}%."
                    ),
                    "before_weight": before_weight,
                    "after_weight_estimate": max_holding,
                    "priority": get_priority(overweight_amount),
                }
            )

    return recommendations


def build_overweight_sector_recommendations(analysis: dict) -> list[dict]:
    risk_inputs = analysis["risk_score"]["inputs"]
    max_sector = risk_inputs["max_sector"]

    recommendations = []

    for sector, sector_weight in analysis["sector_breakdown"].items():
        if sector == "cash":
            continue

        if sector_weight > max_sector:
            overweight_amount = round_value(sector_weight - max_sector)

            recommendations.append(
                {
                    "action": "review",
                    "ticker": None,
                    "amount_or_percent": overweight_amount,
                    "reason_code": "OVERWEIGHT_SECTOR",
                    "human_reason": (
                        f"The {sector} sector is {sector_weight}% of the portfolio, "
                        f"which is above the max sector threshold of {max_sector}%."
                    ),
                    "before_weight": sector_weight,
                    "after_weight_estimate": max_sector,
                    "priority": get_priority(overweight_amount),
                }
            )

    return recommendations


def build_underweight_asset_class_recommendations(analysis: dict) -> list[dict]:
    cash_percentage = analysis["cash_percentage"]
    cash_requirement = get_cash_requirement(analysis)

    if cash_percentage < cash_requirement:
        return [
            {
                "action": "review",
                "ticker": None,
                "amount_or_percent": round_value(cash_requirement - cash_percentage),
                "reason_code": "BELOW_CASH_TARGET",
                "human_reason": (
                    f"Cash is {cash_percentage}% of the portfolio, which is below "
                    f"the {cash_requirement}% cash requirement for this risk tolerance. "
                    "Buy/reallocation suggestions are paused until the cash requirement is met."
                ),
                "before_weight": cash_percentage,
                "after_weight_estimate": cash_requirement,
                "priority": get_priority(cash_requirement - cash_percentage),
            }
        ]

    gap_analysis = analysis["risk_score"]["target_allocation_gap_analysis"]
    recommendations = []

    for gap in gap_analysis:
        if gap["asset_class"] == "cash":
            continue

        if gap["status"] == "underweight":
            underweight_amount = round_value(abs(gap["difference"]))

            recommendations.append(
                {
                    "action": "add_exposure",
                    "ticker": None,
                    "amount_or_percent": underweight_amount,
                    "reason_code": "UNDERWEIGHT_ASSET_CLASS",
                    "human_reason": (
                        f"{gap['asset_class']} is {gap['current_weight']}% of the portfolio, "
                        f"below the target weight of {gap['target_weight']}%. "
                        "This creates a buy/reallocation review signal toward the underweight asset class."
                    ),
                    "before_weight": gap["current_weight"],
                    "after_weight_estimate": gap["target_weight"],
                    "priority": get_priority(underweight_amount),
                }
            )

    return recommendations


def build_optimizer_recommendations(analysis: dict) -> dict:
    recommendations = []

    recommendations.extend(build_overweight_holding_recommendations(analysis))
    recommendations.extend(build_overweight_sector_recommendations(analysis))
    recommendations.extend(build_underweight_asset_class_recommendations(analysis))

    recommendations.sort(
        key=lambda recommendation: recommendation["amount_or_percent"] or 0,
        reverse=True,
    )

    if not recommendations:
        recommendations.append(
            {
                "action": "no_action",
                "ticker": None,
                "amount_or_percent": 0.0,
                "reason_code": "BALANCED_NO_ACTION",
                "human_reason": (
                    "No major overweight holding, overweight sector, or underweight "
                    "asset class signals were detected. Current allocation appears close "
                    "enough to the target allocation for this optimizer version."
                ),
                "before_weight": None,
                "after_weight_estimate": None,
                "priority": "low",
            }
        )

    return {
        "recommendations": recommendations,
        "disclaimer": DISCLAIMER,
    }