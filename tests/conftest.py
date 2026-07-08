import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_portfolio.db"

from backend.api.main import app
from backend.database import Base, get_db
from backend.models import PortfolioRecord, HoldingRecord, PortfolioSnapshot


TEST_DATABASE_URL = "sqlite:///./test_portfolio.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def valid_portfolio_payload():
    return {
        "cash": 2500,
        "holdings": [
            {
                "ticker": "AAPL",
                "quantity": 10,
                "price": 190,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "VTI",
                "quantity": 5,
                "price": 275,
                "asset_class": "etf",
                "sector": "broad market",
            },
        ],
    }


@pytest.fixture()
def saved_portfolio_payload(valid_portfolio_payload):
    return {
        "name": "Test Portfolio",
        **valid_portfolio_payload,
    }


@pytest.fixture()
def invalid_portfolio_payloads():
    return {
        "missing_ticker": {
            "cash": 100,
            "holdings": [
                {
                    "quantity": 1,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        },
        "empty_portfolio": {
            "cash": 100,
            "holdings": [],
        },
        "negative_cash": {
            "cash": -1,
            "holdings": [
                {
                    "ticker": "AAPL",
                    "quantity": 1,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        },
        "zero_quantity": {
            "cash": 100,
            "holdings": [
                {
                    "ticker": "AAPL",
                    "quantity": 0,
                    "price": 100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        },
        "negative_price": {
            "cash": 100,
            "holdings": [
                {
                    "ticker": "AAPL",
                    "quantity": 1,
                    "price": -100,
                    "asset_class": "stock",
                    "sector": "technology",
                }
            ],
        },
    }