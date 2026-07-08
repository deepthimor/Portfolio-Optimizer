from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.portfolio import (
    HoldingInput,
    HoldingRecordResponse,
    HoldingUpdateRequest,
    PortfolioAnalyzeRequest,
    PortfolioAnalyzeResponse,
    PortfolioCreateRequest,
    PortfolioRecordResponse,
    PortfolioUpdateRequest,
)
from backend.services.portfolio_analysis import analyze_portfolio
from backend.services.portfolio_store import (
    create_holding_record,
    create_portfolio_record,
    create_portfolio_snapshot,
    delete_holding_record,
    delete_portfolio_record,
    get_holding_record,
    get_portfolio_record,
    list_portfolio_records,
    list_portfolio_snapshots,
    serialize_portfolio_with_holdings,
    serialize_snapshot,
    update_holding_record,
    update_portfolio_record,
)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/analyze", response_model=PortfolioAnalyzeResponse)
def analyze(request: PortfolioAnalyzeRequest):
    try:
        return analyze_portfolio(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("", response_model=PortfolioRecordResponse)
def create_portfolio(request: PortfolioCreateRequest, db: Session = Depends(get_db)):
    return create_portfolio_record(db, request)


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
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    return create_holding_record(db, portfolio, request)


@router.get("", response_model=list[PortfolioRecordResponse])
def list_portfolios(db: Session = Depends(get_db)):
    return list_portfolio_records(db)


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    return serialize_portfolio_with_holdings(portfolio)


@router.patch("/{portfolio_id}", response_model=PortfolioRecordResponse)
def update_portfolio(
    portfolio_id: int,
    request: PortfolioUpdateRequest,
    db: Session = Depends(get_db),
):
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    return update_portfolio_record(db, portfolio, request)


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    delete_portfolio_record(db, portfolio)

    return {"message": "portfolio deleted"}


@router.patch(
    "/holdings/{holding_id}",
    response_model=HoldingRecordResponse,
)
def update_holding(
    holding_id: int,
    request: HoldingUpdateRequest,
    db: Session = Depends(get_db),
):
    holding = get_holding_record(db, holding_id)

    if not holding:
        raise HTTPException(status_code=404, detail="holding not found")

    return update_holding_record(db, holding, request)


@router.delete("/holdings/{holding_id}")
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
):
    holding = get_holding_record(db, holding_id)

    if not holding:
        raise HTTPException(status_code=404, detail="holding not found")

    delete_holding_record(db, holding)

    return {"message": "holding deleted"}


@router.post("/{portfolio_id}/snapshot")
def create_snapshot(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    snapshot = create_portfolio_snapshot(db, portfolio)

    return serialize_snapshot(snapshot)


@router.get("/{portfolio_id}/snapshots")
def get_snapshots(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = get_portfolio_record(db, portfolio_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="portfolio not found")

    snapshots = list_portfolio_snapshots(db, portfolio_id)

    return [serialize_snapshot(snapshot) for snapshot in snapshots]