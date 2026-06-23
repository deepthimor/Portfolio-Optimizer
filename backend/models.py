from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class PortfolioRecord(Base):
    __tablename__ = "portfolio_records"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cash = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    holdings = relationship(
        "HoldingRecord",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )
    snapshots = relationship(
        "PortfolioSnapshot",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )


class HoldingRecord(Base):
    __tablename__ = "holding_records"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio_records.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    asset_class = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=False)

    portfolio = relationship("PortfolioRecord", back_populates="holdings")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio_records.id"), nullable=False)
    total_portfolio_value = Column(Float, nullable=False)
    total_holdings_value = Column(Float, nullable=False)
    cash_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("PortfolioRecord", back_populates="snapshots")