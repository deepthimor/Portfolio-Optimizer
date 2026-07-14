ALLOWED_AI_SUMMARY_FIELDS = {
    "total_portfolio_value",
    "cash_percentage",
    "number_of_holdings",
    "asset_class_breakdown",
    "sector_breakdown",
    "top_1_percentage",
    "top_3_percentage",
    "top_5_percentage",
    "largest_holding",
    "largest_sector",
    "top_holdings",
    "risk_flags",
    "limitations",
}


AI_SUMMARY_PROMPT_TEMPLATE = """
Summarize only the supplied portfolio metrics.

Rules:
- Do not invent performance.
- Do not assume future returns.
- Do not give personalized financial advice.
- Do not recommend buying, selling, or holding any security.
- Do not use raw secrets, credentials, account numbers, or unsupported data.
- Include uncertainty and limitations.
- Explain the supplied metrics in plain English.

Use only the AI summary input object provided by the backend.
"""


def build_risk_flags(analysis: dict) -> list[str]:
    risk_flags = []

    if analysis["cash_percentage"] > 40:
        risk_flags.append("High cash percentage")

    if analysis["top_1_percentage"] > 30:
        risk_flags.append("High single-holding concentration")

    if analysis["top_3_percentage"] > 60:
        risk_flags.append("High top-three concentration")

    if analysis["top_5_percentage"] > 80:
        risk_flags.append("High top-five concentration")

    if len(analysis["sector_breakdown"]) == 1:
        risk_flags.append("Portfolio is concentrated in one sector")

    return risk_flags


def build_limitations() -> list[str]:
    return [
        "This summary is based only on user-supplied holdings and backend-calculated metrics.",
        "The system does not verify whether ticker symbols are valid securities.",
        "The system does not include historical performance, volatility, valuation, fees, taxes, or user-specific goals.",
        "This is not personalized financial advice.",
    ]


def build_ai_summary_input(analysis: dict) -> dict:
    ai_summary_input = {
        "total_portfolio_value": analysis["total_portfolio_value"],
        "cash_percentage": analysis["cash_percentage"],
        "number_of_holdings": analysis["number_of_holdings"],
        "asset_class_breakdown": analysis["asset_class_breakdown"],
        "sector_breakdown": analysis["sector_breakdown"],
        "top_1_percentage": analysis["top_1_percentage"],
        "top_3_percentage": analysis["top_3_percentage"],
        "top_5_percentage": analysis["top_5_percentage"],
        "largest_holding": analysis["largest_holding"],
        "largest_sector": analysis["largest_sector"],
        "top_holdings": analysis["top_holdings"],
        "risk_flags": build_risk_flags(analysis),
        "limitations": build_limitations(),
    }

    return ai_summary_input


def build_ai_summary_prompt(ai_summary_input: dict) -> str:
    return f"{AI_SUMMARY_PROMPT_TEMPLATE.strip()}\n\nMetrics:\n{ai_summary_input}"


def build_fallback_summary(ai_summary_input: dict) -> str:
    risk_flags = ai_summary_input["risk_flags"]

    if risk_flags:
        risk_text = ", ".join(risk_flags)
    else:
        risk_text = "No major concentration flags were triggered by the current rule set"

    return (
        f"This portfolio has a total value of "
        f"${ai_summary_input['total_portfolio_value']:,.2f}, with "
        f"{ai_summary_input['cash_percentage']}% held in cash. "
        f"The largest holding is {ai_summary_input['largest_holding']}, "
        f"and the largest sector is {ai_summary_input['largest_sector']}. "
        f"Top 1 concentration is {ai_summary_input['top_1_percentage']}%, "
        f"top 3 concentration is {ai_summary_input['top_3_percentage']}%, "
        f"and top 5 concentration is {ai_summary_input['top_5_percentage']}%. "
        f"Risk flags: {risk_text}. "
        f"This summary is based only on supplied portfolio metrics and is not personalized financial advice."
    )