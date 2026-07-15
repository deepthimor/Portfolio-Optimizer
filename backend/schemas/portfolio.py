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


class RiskScoreResponse(BaseModel):
    risk_score_v1: float
    risk_level: str
    concentration_score: float
    diversification_score: float
    sector_exposure_score: float
    cash_score: float
    target_allocation_gap_score: float
    inputs: Dict[str, Any]
    explanations: List[str]


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