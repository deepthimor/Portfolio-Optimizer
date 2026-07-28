from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional


class HoldingInput(BaseModel):
    ticker: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    asset_class: str = Field(..., min_length=1)
    sector: str = Field(..., min_length=1)


class PortfolioAnalyzeRequest(BaseModel):
    cash: float = Field(default=0, ge=0)
    holdings: List[HoldingInput] = Field(..., min_length=1)
    risk_tolerance: Optional[str] = "moderate"
    target_allocation: Optional[Dict[str, float]] = None
    max_holding: Optional[float] = None
    max_sector: Optional[float] = None
    expected_return: Optional[float] = None
    volatility: Optional[float] = None


class HoldingAnalysis(BaseModel):
    ticker: str
    quantity: float
    price: float
    market_value: float
    weight: float
    asset_class: str
    sector: str


class TopHolding(BaseModel):
    ticker: str
    market_value: float
    weight: float
    asset_class: str
    sector: str


class AiSummarySections(BaseModel):
    portfolio_overview: str
    concentration_observations: str
    allocation_observations: str
    educational_note: str
    limitations: str
    risk_flags: str


class AiSummaryResponse(BaseModel):
    is_fallback: bool
    message: str
    sections: AiSummarySections
    disclaimer: str


class TargetAllocationGap(BaseModel):
    asset_class: str
    current_weight: float
    target_weight: float
    difference: float
    status: str


class RiskScoreResponse(BaseModel):
    risk_score_v1: float
    risk_level: str
    concentration_score: float
    diversification_score: float
    sector_exposure_score: float
    cash_score: float
    target_allocation_gap_score: float
    target_allocation_gap_analysis: List[TargetAllocationGap]
    inputs: Dict[str, Any]
    explanations: List[str]

class OptimizerRecommendation(BaseModel):
    action: str
    ticker: Optional[str] = None
    amount_or_percent: Optional[float] = None
    reason_code: str
    human_reason: str
    before_weight: Optional[float] = None
    after_weight_estimate: Optional[float] = None
    priority: str


class OptimizerResponse(BaseModel):
    recommendations: List[OptimizerRecommendation]
    disclaimer: str


class OptimizerExplanationSummary(BaseModel):
    reason_code: str
    summary: str


class OptimizerExplanationResponse(BaseModel):
    is_fallback: bool
    message: str
    prompt_rules: str
    overview: str
    reason_codes: List[str]
    recommendation_summaries: List[OptimizerExplanationSummary]
    limitations: str
    disclaimer: str


class PortfolioAnalyzeResponse(BaseModel):
    total_portfolio_value: float
    total_holdings_value: float
    cash: float
    cash_percentage: float
    number_of_holdings: int
    largest_holding: str
    largest_sector: str
    top_1_percentage: float
    top_3_percentage: float
    top_5_percentage: float
    holdings: List[HoldingAnalysis]
    top_holdings: List[TopHolding]
    sector_breakdown: Dict[str, float]
    asset_class_breakdown: Dict[str, float]
    risk_score: RiskScoreResponse
    optimizer: OptimizerResponse
    optimizer_explanation: OptimizerExplanationResponse
    ai_summary: Optional[AiSummaryResponse] = None
    

class PortfolioCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    cash: float = Field(default=0, ge=0)
    holdings: List[HoldingInput] = Field(default_factory=list)


class PortfolioUpdateRequest(BaseModel):
    name: Optional[str] = None
    cash: Optional[float] = Field(default=None, ge=0)

class HoldingUpdateRequest(BaseModel):
    ticker: Optional[str] = Field(default=None, min_length=1)
    quantity: Optional[float] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    asset_class: Optional[str] = Field(default=None, min_length=1)
    sector: Optional[str] = Field(default=None, min_length=1)


class PortfolioRecordResponse(BaseModel):
    id: int
    name: str
    cash: float

    class Config:
        from_attributes = True


class HoldingRecordResponse(BaseModel):
    id: int
    portfolio_id: int
    ticker: str
    quantity: float
    price: float
    asset_class: str
    sector: str

    class Config:
        from_attributes = True

class ScenarioHoldingImpact(BaseModel):
    ticker: str
    starting_value: float
    scenario_value: float
    dollar_change: float
    percent_change: float
    applied_assumption: str


class ScenarioResult(BaseModel):
    scenario_name: str
    starting_value: float
    scenario_value: float
    dollar_change: float
    percent_change: float
    most_impacted_holdings: List[ScenarioHoldingImpact]
    assumptions: List[str]


class ReportRequest(BaseModel):
    cash: float = Field(default=0, ge=0)
    holdings: List[HoldingInput] = Field(..., min_length=1)
    scenarios: Optional[List[str]] = None


class ReportResult(BaseModel):
    starting_value: float
    results: List[ScenarioResult]
    disclaimer: str

class ReportJobCreateRequest(ReportRequest):
    portfolio_id: Optional[int] = None


class ReportJobCreateResponse(BaseModel):
    job_id: int
    status: str


class ReportJobStatusResponse(BaseModel):
    job_id: int
    portfolio_id: Optional[int] = None
    status: str
    request_json: Dict[str, Any]
    result_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None