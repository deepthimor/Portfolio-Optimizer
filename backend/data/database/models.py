from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    Text, ForeignKey, Index, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

Base = declarative_base()


class SentimentLabel(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class RiskTolerance(str, enum.Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class OrderType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    REBALANCE = "rebalance"


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(ticker='{self.ticker}', company='{self.company_name}')>"


class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    adjusted_close = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    rsi = Column(Float)
    macd = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stock = relationship("Stock", back_populates="prices")
    
    __table_args__ = (
        Index('idx_stock_timestamp', 'stock_id', 'timestamp'),
        Index('idx_unique_stock_price', 'stock_id', 'timestamp', unique=True),
    )
    
    def __repr__(self):
        return f"<StockPrice(stock_id={self.stock_id}, timestamp='{self.timestamp}', close={self.close})>"


class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), unique=True)
    source = Column(String(100))
    author = Column(String(255))
    published_at = Column(DateTime, nullable=False, index=True)
    mentioned_tickers = Column(ARRAY(String))
    sentiment_score = Column(Float)
    sentiment_label = Column(SQLEnum(SentimentLabel))
    sentiment_confidence = Column(Float)
    sentiment_details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_published_at', 'published_at'),
        Index('idx_mentioned_tickers', 'mentioned_tickers', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', sentiment={self.sentiment_label})>"


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False)
    post_id = Column(String(255), unique=True, nullable=False)
    author = Column(String(255))
    title = Column(String(500))
    content = Column(Text, nullable=False)
    url = Column(String(1000))
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    mentioned_tickers = Column(ARRAY(String))
    sentiment_score = Column(Float)
    sentiment_label = Column(SQLEnum(SentimentLabel))
    sentiment_confidence = Column(Float)
    sentiment_details = Column(JSONB)
    posted_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_platform_posted', 'platform', 'posted_at'),
        Index('idx_social_tickers', 'mentioned_tickers', postgresql_using='gin'),
    )


class AggregateSentiment(Base):
    __tablename__ = "aggregate_sentiment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    news_sentiment_avg = Column(Float)
    news_count = Column(Integer, default=0)
    social_sentiment_avg = Column(Float)
    social_count = Column(Integer, default=0)
    combined_sentiment = Column(Float)
    sentiment_label = Column(SQLEnum(SentimentLabel))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_stock_date_sentiment', 'stock_id', 'date', unique=True),
    )


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    predicted_price = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    actual_price = Column(Float)
    prediction_error = Column(Float)
    features_used = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stock = relationship("Stock", back_populates="predictions")
    
    __table_args__ = (
        Index('idx_stock_target_date', 'stock_id', 'target_date'),
        Index('idx_model_predictions', 'model_name', 'prediction_date'),
    )


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    risk_tolerance = Column(SQLEnum(RiskTolerance), nullable=False)
    initial_capital = Column(Float, nullable=False)
    current_value = Column(Float)
    cash_balance = Column(Float)
    total_return = Column(Float)
    total_return_pct = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)
    is_active = Column(Boolean, default=True)
    rebalance_frequency = Column(String(50))
    last_rebalanced_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float)
    current_value = Column(Float)
    unrealized_gain_loss = Column(Float)
    unrealized_gain_loss_pct = Column(Float)
    weight = Column(Float)
    target_weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    __table_args__ = (
        Index('idx_portfolio_stock', 'portfolio_id', 'stock_id', unique=True),
    )


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    transaction_type = Column(SQLEnum(OrderType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    commission = Column(Float, default=0)
    transaction_date = Column(DateTime, nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_portfolio_transaction_date', 'portfolio_id', 'transaction_date'),
    )


class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_value = Column(Float)
    total_return = Column(Float)
    total_return_pct = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    total_trades = Column(Integer)
    parameters = Column(JSONB)
    results = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_strategy_date', 'strategy_name', 'start_date', 'end_date'),
    )


def init_db(engine):
    Base.metadata.create_all(engine)