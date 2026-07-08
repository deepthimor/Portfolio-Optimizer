from backend.models import HoldingRecord, PortfolioRecord, PortfolioSnapshot
from backend.schemas.portfolio import (
    HoldingInput,
    HoldingUpdateRequest,
    PortfolioAnalyzeRequest,
    PortfolioCreateRequest,
    PortfolioUpdateRequest,
)
from backend.services.portfolio_analysis import analyze_portfolio


def create_portfolio_record(db, request: PortfolioCreateRequest):
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


def list_portfolio_records(db):
    return db.query(PortfolioRecord).order_by(PortfolioRecord.id.desc()).all()


def get_portfolio_record(db, portfolio_id: int):
    return db.query(PortfolioRecord).filter(PortfolioRecord.id == portfolio_id).first()


def serialize_portfolio_with_holdings(portfolio: PortfolioRecord):
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


def update_portfolio_record(
    db,
    portfolio: PortfolioRecord,
    request: PortfolioUpdateRequest,
):
    if request.name is not None:
        portfolio.name = request.name

    if request.cash is not None:
        portfolio.cash = request.cash

    db.commit()
    db.refresh(portfolio)
    return portfolio


def delete_portfolio_record(db, portfolio: PortfolioRecord):
    db.delete(portfolio)
    db.commit()


def create_holding_record(db, portfolio: PortfolioRecord, request: HoldingInput):
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


def get_holding_record(db, holding_id: int):
    return db.query(HoldingRecord).filter(HoldingRecord.id == holding_id).first()


def update_holding_record(
    db,
    holding: HoldingRecord,
    request: HoldingUpdateRequest,
):
    if request.ticker is not None:
        holding.ticker = request.ticker.upper().strip()

    if request.quantity is not None:
        holding.quantity = request.quantity

    if request.price is not None:
        holding.price = request.price

    if request.asset_class is not None:
        holding.asset_class = request.asset_class.lower().strip()

    if request.sector is not None:
        holding.sector = request.sector.lower().strip()

    db.commit()
    db.refresh(holding)
    return holding


def delete_holding_record(db, holding: HoldingRecord):
    db.delete(holding)
    db.commit()


def create_portfolio_snapshot(db, portfolio: PortfolioRecord):
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
    return snapshot


def list_portfolio_snapshots(db, portfolio_id: int):
    return (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.portfolio_id == portfolio_id)
        .order_by(PortfolioSnapshot.created_at.desc())
        .all()
    )


def serialize_snapshot(snapshot: PortfolioSnapshot):
    return {
        "id": snapshot.id,
        "portfolio_id": snapshot.portfolio_id,
        "total_portfolio_value": snapshot.total_portfolio_value,
        "total_holdings_value": snapshot.total_holdings_value,
        "cash_percentage": snapshot.cash_percentage,
        "created_at": snapshot.created_at,
    }