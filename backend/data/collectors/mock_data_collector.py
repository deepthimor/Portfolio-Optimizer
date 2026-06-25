import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockDataCollector:
    
    def __init__(self):
        logger.info("mock data collector initialized")
    
    def generate_stock_data(self, ticker: str, days: int = 365) -> pd.DataFrame:
        
        logger.info(f"generating mock data for {ticker}")
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        np.random.seed(hash(ticker) % 2**32)
        base_price = np.random.uniform(50, 500)
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * np.random.uniform(0.99, 1.01, days),
            'high': prices * np.random.uniform(1.00, 1.03, days),
            'low': prices * np.random.uniform(0.97, 1.00, days),
            'close': prices,
            'volume': np.random.randint(1000000, 100000000, days),
            'adjusted_close': prices,
            'ticker': ticker
        })
        
        logger.info(f"generated {len(df)} rows for {ticker}")
        return df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        
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
    
    def collect_historical_data(
        self,
        tickers: List[str],
        days: int = 365
    ) -> Dict[str, pd.DataFrame]:
        
        results = {}
        
        logger.info(f"generating data for {len(tickers)} stocks")
        
        for ticker in tqdm(tickers, desc="generating stock data"):
            try:
                df = self.generate_stock_data(ticker, days)
                df = self.calculate_technical_indicators(df)
                results[ticker] = df
                
            except Exception as e:
                logger.error(f"failed to generate data for {ticker}: {str(e)}")
                continue
        
        logger.info(f"generation complete. created data for {len(results)} stocks")
        return results


if __name__ == "__main__":
    test_tickers = ["AAPL", "GOOGL", "MSFT"]
    
    collector = MockDataCollector()
    results = collector.collect_historical_data(test_tickers, days=365)
    
    for ticker, df in results.items():
        print(f"\n{ticker}:")
        print(df[['timestamp', 'close', 'sma_20', 'rsi']].tail())