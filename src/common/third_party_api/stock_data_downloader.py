from datetime import datetime
import polars as pl

from common.third_party_api.stock_data_api import StockDataApi



class StockDataDownloader:
    def __init__(self, api: StockDataApi):
        """
        Initializes the downloader with a specific Api strategy.
        - api: An instance of a class that implements the StockDataApi interface.
        """
        self.api = api

    def download_data(self, ticker: str, start_date: datetime, end_date: datetime, interval: str) -> pl.DataFrame:
        """
        Downloads stock data using the selected Api strategy.
        - ticker: The stock symbol (e.g., 'AAPL').
        - start_date: The starting date for the data.
        - end_date: The ending date for the data.
        - interval: The data interval (e.g., '1d', '1h', '5m').
        Returns: Polars DataFrame with stock data.
        """
        return self.api.fetch_data(ticker, start_date, end_date, interval)
