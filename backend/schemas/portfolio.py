from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class HoldingInput(BaseModel):
    ticker: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    asset_class: str = Field(..., min_length=1)
    sector: str = Field(..., min_length=1)


class PortfolioAnalyzeRequest(BaseModel):
    cash: float = Field(default=0, ge=0)
    holdings: List[HoldingInput] = Field(..., min_length=1)


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


class PortfolioAnalyzeResponse(BaseModel):
    total_portfolio_value: float
    total_holdings_value: float
    cash: float
    cash_percentage: float
    holdings: List[HoldingAnalysis]
    top_holdings: List[TopHolding]
    sector_breakdown: Dict[str, float]
    asset_class_breakdown: Dict[str, float]
    

class PortfolioCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    cash: float = Field(default=0, ge=0)
    holdings: List[HoldingInput] = Field(default_factory=list)


class PortfolioUpdateRequest(BaseModel):
    name: Optional[str] = None
    cash: Optional[float] = Field(default=None, ge=0)


class PortfolioRecordResponse(BaseModel):
    id: int
    name: str
    cash: float

    class Config:
        from_attributes = True