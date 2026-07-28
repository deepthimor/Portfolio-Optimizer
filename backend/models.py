from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
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

class ReportJob(Base):
    __tablename__ = "report_jobs"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio_records.id"), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    request_json = Column(JSON, nullable=False)
    result_json = Column(JSON, nullable=True)
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )