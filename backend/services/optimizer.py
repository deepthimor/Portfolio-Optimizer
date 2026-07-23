DISCLAIMER = "Educational information only; not financial advice."

REASON_CODES = {
    "OVERWEIGHT_HOLDING",
    "OVERWEIGHT_SECTOR",
    "BELOW_CASH_TARGET",
    "UNDERWEIGHT_ASSET_CLASS",
    "BALANCED_NO_ACTION",
}


def round_value(value: float) -> float:
    return round(value, 2)


def get_priority(overweight_amount: float) -> str:
    if overweight_amount >= 15:
        return "high"
    if overweight_amount >= 5:
        return "medium"
    return "low"


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


def build_optimizer_recommendations(analysis: dict) -> dict:
    recommendations = []

    recommendations.extend(build_overweight_holding_recommendations(analysis))
    recommendations.extend(build_overweight_sector_recommendations(analysis))

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
                    "No overweight holding or overweight sector signals were detected."
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