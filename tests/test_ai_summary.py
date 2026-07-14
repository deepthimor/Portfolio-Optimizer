from backend.services.ai_summary import (
    ALLOWED_AI_SUMMARY_FIELDS,
    AI_SUMMARY_PROMPT_TEMPLATE,
    build_ai_summary_input,
    build_ai_summary_prompt,
    build_fallback_summary,
)


def sample_analysis():
    return {
        "total_portfolio_value": 10000,
        "total_holdings_value": 9000,
        "cash": 1000,
        "cash_percentage": 10,
        "number_of_holdings": 3,
        "largest_holding": "AAPL",
        "largest_sector": "technology",
        "top_1_percentage": 35,
        "top_3_percentage": 90,
        "top_5_percentage": 90,
        "holdings": [
            {
                "ticker": "AAPL",
                "quantity": 10,
                "price": 100,
                "market_value": 1000,
                "weight": 35,
                "asset_class": "stock",
                "sector": "technology",
            }
        ],
        "top_holdings": [
            {
                "ticker": "AAPL",
                "market_value": 1000,
                "weight": 35,
                "asset_class": "stock",
                "sector": "technology",
            }
        ],
        "sector_breakdown": {"technology": 90},
        "asset_class_breakdown": {"stock": 90},
    }


def test_ai_summary_input_contains_only_allowed_fields():
    ai_summary_input = build_ai_summary_input(sample_analysis())

    assert set(ai_summary_input.keys()) == ALLOWED_AI_SUMMARY_FIELDS


def test_ai_summary_input_excludes_raw_holdings_cash_and_prices():
    ai_summary_input = build_ai_summary_input(sample_analysis())

    assert "holdings" not in ai_summary_input
    assert "cash" not in ai_summary_input
    assert "total_holdings_value" not in ai_summary_input
    assert "price" not in str(ai_summary_input)
    assert "quantity" not in str(ai_summary_input)


def test_ai_summary_input_includes_required_metrics():
    ai_summary_input = build_ai_summary_input(sample_analysis())

    assert ai_summary_input["total_portfolio_value"] == 10000
    assert ai_summary_input["cash_percentage"] == 10
    assert ai_summary_input["number_of_holdings"] == 3
    assert ai_summary_input["largest_holding"] == "AAPL"
    assert ai_summary_input["largest_sector"] == "technology"
    assert ai_summary_input["top_1_percentage"] == 35
    assert ai_summary_input["top_3_percentage"] == 90
    assert ai_summary_input["top_5_percentage"] == 90


def test_ai_summary_input_includes_risk_flags_and_limitations():
    ai_summary_input = build_ai_summary_input(sample_analysis())

    assert "High single-holding concentration" in ai_summary_input["risk_flags"]
    assert "High top-three concentration" in ai_summary_input["risk_flags"]
    assert len(ai_summary_input["limitations"]) > 0


def test_prompt_template_sets_clear_boundaries():
    assert "Summarize only the supplied portfolio metrics" in AI_SUMMARY_PROMPT_TEMPLATE
    assert "Do not invent performance" in AI_SUMMARY_PROMPT_TEMPLATE
    assert "Do not give personalized financial advice" in AI_SUMMARY_PROMPT_TEMPLATE
    assert "Include uncertainty and limitations" in AI_SUMMARY_PROMPT_TEMPLATE


def test_ai_summary_prompt_uses_only_summary_input():
    ai_summary_input = build_ai_summary_input(sample_analysis())
    prompt = build_ai_summary_prompt(ai_summary_input)

    assert "Metrics:" in prompt
    assert "AAPL" in prompt
    assert "quantity" not in prompt
    assert "price" not in prompt


def test_fallback_summary_is_created_without_ai():
    ai_summary_input = build_ai_summary_input(sample_analysis())
    fallback = build_fallback_summary(ai_summary_input)

    assert "This portfolio has a total value" in fallback
    assert "not personalized financial advice" in fallback
    assert "top 3 concentration" in fallback