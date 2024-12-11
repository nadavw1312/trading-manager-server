import yfinance as yf
from datetime import datetime
import polars as pl

from common.third_party_api.stock_data_api import StockDataApi



class YahooFinanceApi(StockDataApi):
    yfinance_timeframes = [
    "1m",   # 1 minute
    "2m",   # 2 minutes
    "5m",   # 5 minutes
    "15m",  # 15 minutes
    "30m",  # 30 minutes
    "60m",  # 1 hour
    "90m",  # 90 minutes
    "1d",   # 1 day
    "5d",   # 5 days
    "1wk",  # 1 week
    "1mo",  # 1 month
    "3mo"   # 3 months
]

    def get_stock_metadata(self,stock_name:str):
        stock = yf.Ticker(stock_name)
        info = stock.info
        ticker = {
            'ticker': info.get('symbol'),
            'shortName': info.get('shortName'),
            'longName': info.get('longName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'marketCap': info.get('marketCap'),
            'website': info.get('website'),
            'country': info.get('country'),
            'currency': info.get('currency'),
            'description': info.get('longBusinessSummary'),  # Add company description
            'CEO': info.get('ceo'),  # CEO of the company
            'employees': info.get('fullTimeEmployees'),  # Number of employees
            'headquarters': info.get('city') + ', ' + info.get('state') if info.get('city') and info.get('state') else info.get('city')  # Headquarters
        }
        
        return ticker

    def get_stocks_metadata(self,stock_names:list):
        return [self.get_stock_metadata(name) for name in stock_names]

    def fetch_data(self, ticker: str, start_date: datetime, end_date: datetime, interval: str) -> pl.DataFrame:
        """
        Fetch stock data from Yahoo Finance and return as a Polars DataFrame.
        - ticker: The stock symbol (e.g., 'AAPL').
        - start_date: The starting date for the data.
        - end_date: The ending date for the data.
        - interval: The data interval (e.g., '1d', '1h', '5m').
        Returns: Polars DataFrame with stock data.
        """
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        stock_data["Datetime"] = stock_data.index
        
        # Convert Pandas DataFrame to Polars DataFrame
        return pl.from_pandas(stock_data)
