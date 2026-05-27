import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import logging

from backend.data.database.models import Base, Stock, init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("database_url not found in .env file")
        logger.error("make sure you have a .env file with database_url set")
        sys.exit(1)
    
    logger.info("environment variables loaded")
    return database_url


def test_connection(database_url: str) -> bool:
    try:
        logger.info("testing database connection")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("database connection successful")
        return True
        
    except OperationalError as e:
        logger.error(f"database connection failed: {str(e)}")
        logger.error("\ncommon fixes:")
        logger.error("1. make sure postgresql is running: docker-compose up -d postgres")
        logger.error("2. check your database_url in .env")
        logger.error("3. verify database exists")
        return False
    
    except Exception as e:
        logger.error(f"unexpected error: {str(e)}")
        return False


def create_database_if_not_exists(database_url: str):
    try:
        db_name = database_url.split('/')[-1]
        base_url = database_url.rsplit('/', 1)[0] + '/postgres'
        engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.fetchone()
            
            if not exists:
                logger.info(f"creating database '{db_name}'")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"database '{db_name}' created successfully")
            else:
                logger.info(f"database '{db_name}' already exists")
        
    except Exception as e:
        logger.warning(f"could not create database: {str(e)}")
        logger.warning("if database doesn't exist, create it manually")


def create_tables(database_url: str):
    try:
        logger.info("creating database tables")
        engine = create_engine(database_url)
        
        Base.metadata.create_all(engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"created {len(tables)} tables:")
        for table in sorted(tables):
            logger.info(f"   - {table}")
        
        return True
        
    except Exception as e:
        logger.error(f"error creating tables: {str(e)}")
        return False


def seed_initial_data(database_url: str):
    try:
        logger.info("seeding initial data")
        
        from sqlalchemy.orm import sessionmaker
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        initial_stocks = [
            {"ticker": "AAPL", "company_name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
            {"ticker": "GOOGL", "company_name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Content & Information"},
            {"ticker": "MSFT", "company_name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
            {"ticker": "AMZN", "company_name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
            {"ticker": "TSLA", "company_name": "Tesla Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
            {"ticker": "META", "company_name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Internet Content & Information"},
            {"ticker": "NVDA", "company_name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
            {"ticker": "JPM", "company_name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks"},
            {"ticker": "V", "company_name": "Visa Inc.", "sector": "Financial Services", "industry": "Credit Services"},
            {"ticker": "WMT", "company_name": "Walmart Inc.", "sector": "Consumer Defensive", "industry": "Discount Stores"},
        ]
        
        added_count = 0
        for stock_data in initial_stocks:
            existing = session.query(Stock).filter_by(ticker=stock_data["ticker"]).first()
            if not existing:
                stock = Stock(**stock_data)
                session.add(stock)
                added_count += 1
        
        session.commit()
        session.close()
        
        logger.info(f"added {added_count} stocks to database")
        
    except Exception as e:
        logger.error(f"error seeding data: {str(e)}")


def verify_setup(database_url: str):
    try:
        logger.info("verifying setup")
        
        from sqlalchemy.orm import sessionmaker
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        stock_count = session.query(Stock).count()
        logger.info(f"found {stock_count} stocks in database")
        
        if stock_count > 0:
            sample_stock = session.query(Stock).first()
            logger.info(f"sample stock: {sample_stock.ticker} - {sample_stock.company_name}")
        
        session.close()
        logger.info("verification complete")
        return True
        
    except Exception as e:
        logger.error(f"verification failed: {str(e)}")
        return False


def main():
    logger.info("starting database setup")
    
    database_url = load_environment()
    
    create_database_if_not_exists(database_url)
    
    if not test_connection(database_url):
        logger.error("cannot proceed without database connection")
        sys.exit(1)
    
    if not create_tables(database_url):
        logger.error("failed to create tables")
        sys.exit(1)
    
    response = input("\nseed database with initial stocks? (y/n): ").lower()
    if response == 'y':
        seed_initial_data(database_url)
    
    if verify_setup(database_url):
        logger.info("database setup complete")
        logger.info(f"\nnext steps:")
        logger.info("1. run data collection: python scripts/collect_historical_data.py")
        logger.info("2. start api server: uvicorn backend.api.main:app --reload")
    else:
        logger.error("setup verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()