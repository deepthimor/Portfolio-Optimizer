import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockDataCollector:
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        logger.info("stock data collector initialized")
    
    def fetch_stock_data(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str,
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        
        try:
            logger.info(f"fetching {ticker} data from {start_date} to {end_date}")
            
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False
            )
            
            if df.empty:
                logger.warning(f"no data found for {ticker}")
                return None
            
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adjusted_close'
            })
            
            df['ticker'] = ticker
            
            logger.info(f"fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"error fetching {ticker}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        
        try:
            logger.info("calculating technical indicators")
            df = df.copy()
            
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            df['daily_return'] = df['close'].pct_change()
            df['volatility'] = df['daily_return'].rolling(window=20).std()
            
            logger.info("technical indicators calculated")
            return df
            
        except Exception as e:
            logger.error(f"error calculating indicators: {str(e)}")
            return df
    
    def get_stock_info(self, ticker: str) -> Dict:
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', None)
            }
        except Exception as e:
            logger.error(f"error fetching info for {ticker}: {str(e)}")
            return {
                'ticker': ticker,
                'company_name': ticker,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': None
            }
    
    def save_to_database(self, df: pd.DataFrame, stock_id: int):
        
        try:
            logger.info(f"saving {len(df)} rows to database")
            
            df_to_save = df[[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'adjusted_close', 'sma_20', 'sma_50', 'rsi', 'macd'
            ]].copy()
            
            df_to_save['stock_id'] = stock_id
            df_to_save['created_at'] = datetime.utcnow()
            
            df_to_save.to_sql(
                'stock_prices',
                self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            logger.info(f"saved {len(df)} rows successfully")
            
        except Exception as e:
            logger.error(f"error saving to database: {str(e)}")
            raise
    
    def collect_historical_data(
        self,
        tickers: List[str],
        years: int = 5,
        save_to_db: bool = True
    ) -> Dict[str, pd.DataFrame]:
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        results = {}
        
        logger.info(f"collecting data for {len(tickers)} stocks from {start_str} to {end_str}")
        
        for ticker in tqdm(tickers, desc="collecting stock data"):
            try:
                df = self.fetch_stock_data(ticker, start_str, end_str)
                
                if df is None or df.empty:
                    logger.warning(f"skipping {ticker} - no data")
                    continue
                
                df = self.calculate_technical_indicators(df)
                
                results[ticker] = df
                
                if save_to_db:
                    logger.info(f"saving {ticker} to database not yet implemented")
                
            except Exception as e:
                logger.error(f"failed to collect data for {ticker}: {str(e)}")
                continue
        
        logger.info(f"collection complete. collected data for {len(results)} stocks")
        return results


def quick_fetch(ticker: str, days: int = 30) -> pd.DataFrame:
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    collector = StockDataCollector(database_url="sqlite:///:memory:")
    df = collector.fetch_stock_data(
        ticker,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        df = collector.calculate_technical_indicators(df)
    
    return df


if __name__ == "__main__":
    test_tickers = ["AAPL", "GOOGL", "MSFT"]
    
    collector = StockDataCollector(database_url="sqlite:///:memory:")
    results = collector.collect_historical_data(test_tickers, years=1, save_to_db=False)
    
    for ticker, df in results.items():
        print(f"\n{ticker}:")
        print(df[['timestamp', 'close', 'sma_20', 'rsi']].tail())