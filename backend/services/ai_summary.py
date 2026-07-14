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
        "This is educational information only and not personalized financial advice.",
    ]


def build_ai_summary_input(analysis: dict) -> dict:
    return {
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


def build_ai_summary_prompt(ai_summary_input: dict) -> str:
    return f"{AI_SUMMARY_PROMPT_TEMPLATE.strip()}\n\nMetrics:\n{ai_summary_input}"


def build_ai_summary_sections(ai_summary_input: dict) -> dict:
    risk_flags = ai_summary_input["risk_flags"]

    if risk_flags:
        risk_text = ", ".join(risk_flags)
    else:
        risk_text = "No major concentration flags were triggered by the current rule set."

    return {
        "portfolio_overview": (
            f"Total portfolio value is "
            f"${ai_summary_input['total_portfolio_value']:,.2f}. "
            f"The portfolio has {ai_summary_input['number_of_holdings']} holdings "
            f"and {ai_summary_input['cash_percentage']}% held in cash."
        ),
        "concentration_observations": (
            f"Top 1 concentration is {ai_summary_input['top_1_percentage']}%, "
            f"top 3 concentration is {ai_summary_input['top_3_percentage']}%, "
            f"and top 5 concentration is {ai_summary_input['top_5_percentage']}%. "
            f"The largest holding is {ai_summary_input['largest_holding']}."
        ),
        "allocation_observations": (
            f"The largest sector is {ai_summary_input['largest_sector']}. "
            f"Asset allocation is {ai_summary_input['asset_class_breakdown']}. "
            f"Sector allocation is {ai_summary_input['sector_breakdown']}."
        ),
        "educational_note": (
            "Educational information only; not financial advice. "
            "This summary explains supplied metrics and does not recommend buying, selling, or holding any security."
        ),
        "limitations": " ".join(ai_summary_input["limitations"]),
        "risk_flags": risk_text,
    }


def build_fallback_summary(ai_summary_input: dict) -> dict:
    sections = build_ai_summary_sections(ai_summary_input)

    return {
        "is_fallback": True,
        "message": "AI summary unavailable; deterministic metrics still shown.",
        "sections": sections,
        "disclaimer": "Educational information only; not financial advice.",
    }


def build_safe_ai_summary(analysis: dict, force_failure: bool = False) -> dict:
    ai_summary_input = build_ai_summary_input(analysis)

    try:
        if force_failure:
            raise RuntimeError("AI summary generation unavailable")

        return {
            "is_fallback": False,
            "message": "AI summary generated from deterministic metrics.",
            "sections": build_ai_summary_sections(ai_summary_input),
            "disclaimer": "Educational information only; not financial advice.",
        }
    except Exception as error:
        print(f"AI summary failed: {error}")
        return build_fallback_summary(ai_summary_input)