import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging
from tqdm import tqdm
import time
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlphaVantageCollector:
    
    def __init__(self, api_key: str, database_url: str = None):
        self.api_key = api_key
        self.ts = TimeSeries(key=api_key, output_format='pandas')
        
        if database_url:
            self.database_url = database_url
            self.engine = create_engine(database_url)
        else:
            self.database_url = None
            self.engine = None
        
        logger.info("alpha vantage collector initialized")
    
    def fetch_stock_data(
        self, 
        ticker: str,
        outputsize: str = 'full'
    ) -> Optional[pd.DataFrame]:
        
        try:
            logger.info(f"fetching {ticker} data from alpha vantage")
            
            data, meta_data = self.ts.get_daily_adjusted(
                symbol=ticker,
                outputsize=outputsize
            )
            
            if data.empty:
                logger.warning(f"no data found for {ticker}")
                return None
            
            df = data.reset_index()
            df = df.rename(columns={
                'date': 'timestamp',
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. adjusted close': 'adjusted_close',
                '6. volume': 'volume'
            })
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume']]
            df['ticker'] = ticker
            df = df.sort_values('timestamp')
            
            logger.info(f"fetched {len(df)} rows for {ticker}")
            
            time.sleep(12)
            
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
    
    def collect_historical_data(
        self,
        tickers: List[str],
        save_to_db: bool = False
    ) -> Dict[str, pd.DataFrame]:
        
        results = {}
        
        logger.info(f"collecting data for {len(tickers)} stocks")
        
        for ticker in tqdm(tickers, desc="collecting stock data"):
            try:
                df = self.fetch_stock_data(ticker)
                
                if df is None or df.empty:
                    logger.warning(f"skipping {ticker} - no data")
                    continue
                
                df = self.calculate_technical_indicators(df)
                
                results[ticker] = df
                
                if save_to_db and self.engine:
                    logger.info(f"saving {ticker} to database not yet implemented")
                
            except Exception as e:
                logger.error(f"failed to collect data for {ticker}: {str(e)}")
                continue
        
        logger.info(f"collection complete. collected data for {len(results)} stocks")
        return results


if __name__ == "__main__":
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    if not api_key:
        logger.error("ALPHA_VANTAGE_API_KEY not found in .env file")
        exit(1)
    
    test_tickers = ["AAPL", "GOOGL", "MSFT"]
    
    collector = AlphaVantageCollector(api_key=api_key)
    results = collector.collect_historical_data(test_tickers, save_to_db=False)
    
    for ticker, df in results.items():
        print(f"\n{ticker}:")
        print(df[['timestamp', 'close', 'sma_20', 'rsi']].tail())