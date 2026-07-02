from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import HoldingRecord, PortfolioRecord, PortfolioSnapshot
from backend.schemas.portfolio import (
    HoldingInput,
    HoldingRecordResponse,
    PortfolioAnalyzeRequest,
    PortfolioAnalyzeResponse,
    PortfolioCreateRequest,
    PortfolioRecordResponse,
    PortfolioUpdateRequest,
)
from backend.services.portfolio_analysis import analyze_portfolio

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/analyze", response_model=PortfolioAnalyzeResponse)
def analyze(request: PortfolioAnalyzeRequest):
    try:
        return analyze_portfolio(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("", response_model=PortfolioRecordResponse)
def create_portfolio(request: PortfolioCreateRequest, db: Session = Depends(get_db)):
    portfolio = PortfolioRecord(name=request.name, cash=request.cash)
    db.add(portfolio)
    db.flush()

    for holding in request.holdings:
        db.add(
            HoldingRecord(
                portfolio_id=portfolio.id,
                ticker=holding.ticker.upper().strip(),
                quantity=holding.quantity,
                price=holding.price,
                asset_class=holding.asset_class.lower().strip(),
                sector=holding.sector.lower().strip(),
            )
        )

    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingRecordResponse,
    status_code=201,
)
def create_holding(
    portfolio_id: int,
    request: HoldingInput,
    db: Session = Depends(get_db),
):
    portfolio = (
        db.query(PortfolioRecord)
        .filter(PortfolioRecord.id == portfolio_id)
        .first()
    )

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    holding = HoldingRecord(
        portfolio_id=portfolio.id,
        ticker=request.ticker.upper().strip(),
        quantity=request.quantity,
        price=request.price,
        asset_class=request.asset_class.lower().strip(),
        sector=request.sector.lower().strip(),
    )

    db.add(holding)
    db.commit()
    db.refresh(holding)

    return holding


@router.get("", response_model=list[PortfolioRecordResponse])
def list_portfolios(db: Session = Depends(get_db)):
    return db.query(PortfolioRecord).order_by(PortfolioRecord.id.desc()).all()


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioRecord).filter(PortfolioRecord.id == portfolio_id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "cash": portfolio.cash,
        "holdings": [
            {
                "id": holding.id,
                "ticker": holding.ticker,
                "quantity": holding.quantity,
                "price": holding.price,
                "asset_class": holding.asset_class,
                "sector": holding.sector,
            }
            for holding in portfolio.holdings
        ],
    }


@router.patch("/{portfolio_id}", response_model=PortfolioRecordResponse)
def update_portfolio(
    portfolio_id: int,
    request: PortfolioUpdateRequest,
    db: Session = Depends(get_db),
):
    portfolio = db.query(PortfolioRecord).filter(PortfolioRecord.id == portfolio_id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    if request.name is not None:
        portfolio.name = request.name

    if request.cash is not None:
        portfolio.cash = request.cash

    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioRecord).filter(PortfolioRecord.id == portfolio_id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    db.delete(portfolio)
    db.commit()

    return {"message": "portfolio deleted"}


@router.post("/{portfolio_id}/snapshot")
def create_snapshot(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioRecord).filter(PortfolioRecord.id == portfolio_id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    request = PortfolioAnalyzeRequest(
        cash=portfolio.cash,
        holdings=[
            {
                "ticker": holding.ticker,
                "quantity": holding.quantity,
                "price": holding.price,
                "asset_class": holding.asset_class,
                "sector": holding.sector,
            }
            for holding in portfolio.holdings
        ],
    )

    analysis = analyze_portfolio(request)

    snapshot = PortfolioSnapshot(
        portfolio_id=portfolio.id,
        total_portfolio_value=analysis["total_portfolio_value"],
        total_holdings_value=analysis["total_holdings_value"],
        cash_percentage=analysis["cash_percentage"],
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "id": snapshot.id,
        "portfolio_id": snapshot.portfolio_id,
        "total_portfolio_value": snapshot.total_portfolio_value,
        "total_holdings_value": snapshot.total_holdings_value,
        "cash_percentage": snapshot.cash_percentage,
        "created_at": snapshot.created_at,
    }