"""Optimizer explanation layer.

This module explains deterministic optimizer recommendations.

Important boundary:
- Deterministic recommendations must be generated first.
- Any AI/LLM explanation may only explain existing recommendations.
- The explanation must cite reason codes.
- The explanation must not invent returns, prices, risk-adjusted performance, or new recommendations.
- The explanation must not tell users to buy or sell anything beyond the deterministic optimizer output.
"""

OPTIMIZER_EXPLANATION_DISCLAIMER = "Educational information only; not financial advice."


OPTIMIZER_EXPLANATION_PROMPT_RULES = """
You are explaining deterministic portfolio optimizer recommendations.

Rules:
1. Only explain recommendations already produced by the backend optimizer.
2. Cite the reason_code for each recommendation you discuss.
3. Do not invent expected returns, future prices, alpha, Sharpe ratio, or performance forecasts.
4. Do not recommend buying or selling anything beyond the deterministic recommendation objects.
5. Use educational language such as review, consider, allocation signal, concentration signal, and reallocation signal.
6. Include limitations.
7. Remind the user this is educational information only and not financial advice.
"""


def build_optimizer_explanation(optimizer: dict) -> dict:
    recommendations = optimizer.get("recommendations", [])

    if not recommendations:
        return build_optimizer_explanation_fallback()

    reason_codes = [
        recommendation.get("reason_code", "UNKNOWN_REASON")
        for recommendation in recommendations
    ]

    overview = (
        "The optimizer explanation is based only on deterministic backend "
        "recommendations that were already generated."
    )

    recommendation_summaries = []

    for recommendation in recommendations:
        reason_code = recommendation.get("reason_code")
        action = recommendation.get("action")
        human_reason = recommendation.get("human_reason")
        priority = recommendation.get("priority")

        recommendation_summaries.append(
            {
                "reason_code": reason_code,
                "summary": (
                    f"{reason_code}: The optimizer produced an action of "
                    f"{action} with {priority} priority. {human_reason}"
                ),
            }
        )

    limitations = (
        "This explanation is limited to user-provided holdings and deterministic "
        "portfolio metrics. It does not use live market data, expected returns, "
        "tax impact, transaction costs, account type, or personal financial goals."
    )

    return {
        "is_fallback": False,
        "message": "Optimizer explanation generated from deterministic recommendations.",
        "prompt_rules": OPTIMIZER_EXPLANATION_PROMPT_RULES,
        "overview": overview,
        "reason_codes": reason_codes,
        "recommendation_summaries": recommendation_summaries,
        "limitations": limitations,
        "disclaimer": OPTIMIZER_EXPLANATION_DISCLAIMER,
    }


def build_optimizer_explanation_fallback() -> dict:
    return {
        "is_fallback": True,
        "message": (
            "Optimizer explanation unavailable. Deterministic recommendations "
            "are still shown."
        ),
        "prompt_rules": OPTIMIZER_EXPLANATION_PROMPT_RULES,
        "overview": (
            "The optimizer explanation could not be generated, but the backend "
            "recommendation objects remain available."
        ),
        "reason_codes": [],
        "recommendation_summaries": [],
        "limitations": (
            "This fallback does not add any new portfolio interpretation. "
            "Use the structured optimizer recommendations instead."
        ),
        "disclaimer": OPTIMIZER_EXPLANATION_DISCLAIMER,
    }