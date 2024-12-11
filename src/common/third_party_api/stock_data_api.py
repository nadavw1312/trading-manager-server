from abc import ABC, abstractmethod
from datetime import datetime
import polars as pl

class StockDataApi(ABC):
    @abstractmethod
    def fetch_data(self, ticker: str, start_date: datetime, end_date: datetime, interval: str) -> pl.DataFrame:
        """
        Fetch stock data from a specific start date to end date with a given interval.
        - ticker: The stock symbol (e.g., 'AAPL').
        - start_date: The starting date for the data.
        - end_date: The ending date for the data.
        - interval: The data interval (e.g., '1d', '1h', '5m').
        Returns: Polars DataFrame with stock data.
        """
        pass
