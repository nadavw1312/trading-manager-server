from datetime import date, datetime, timedelta
from typing import Any, Dict, List
from bson import ObjectId

from common.base.base_mongo_bl import BaseMongoBl

import polars as pl

from server.src.common.services.models.candles_model import CandleModel
from common.third_party_api.stock_data_downloader import StockDataDownloader
from common.third_party_api.yahoo_finance_api import YahooFinanceApi
from features.big_data.candles.candles_dal import CandlesDal
from features.stocks.stocks_bl import StocksBl
from server.src.common.services.models.stock_model import StockModel


# List of all timeframes supported by yfinance
yfinance_timeframes = YahooFinanceApi.yfinance_timeframes

class CandlesBl(BaseMongoBl[CandlesDal, CandleModel]):
    def __init__(self):
        super().__init__(CandlesDal)
        self.api = StockDataDownloader(YahooFinanceApi())  # Api instance for fetching stock data
        
    def _to_df(self,candles:List[CandleModel],timeframe:str)->pl.DataFrame:
        candles_df = []
        for candle in candles:
            candle = {
                "Datetime": candle.datetime,
                "Open": candle.open,
                "High": candle.high,
                "Low": candle.low,
                "Close": candle.close,
                "Volume": candle.volume,
                "timeframe": timeframe
                }
            candles_df.append(candle)
        return pl.DataFrame(candles_df)

    def sync_candles_for_all_timeframes(self,stocks:List[StockModel]):
        """
        Sync candles for all supported timeframes for all stocks.
        """
        # Loop over all supported timeframes
        print("Starting sync for all timeframes...")
        for timeframe in yfinance_timeframes:
            print(f"Syncing candles for timeframe: {timeframe}")
            self.sync_candles_for_all_stock(stocks,timeframe)

    def sync_candles_for_all_stock(self,stocks:List[StockModel], timeframe: str = '1d'):
        """
        Sync candles for all stocks by their tickers for a given timeframe.
        Fetches the last 2 years of candle data, avoiding duplicates.
        """
        print(f"Syncing {len(stocks)} stocks for timeframe {timeframe}")
        for stock in stocks:
            print(f"Syncing {stock.ticker}...")
            self.sync_candles(str(stock.id), stock.ticker, timeframe)

    def sync_candles(self, stock_id: str, ticker: str, timeframe: str):
        """
        Sync candlestick data for a stock based on timeframe.
        Prevent duplicates by checking for existing candles in bulk.
        """
        end_date = datetime.now()
        
        # Set appropriate start date based on timeframe
        if timeframe in ['1d', '5d', '1wk', '1mo', '3mo']:
            start_date = end_date - timedelta(days=720)  # 2 years
        elif timeframe in ['90m', '60m', '30m', '15m', '5m']:
            start_date = end_date - timedelta(days=59)  # 60 days
        else:
            start_date = end_date - timedelta(days=6)  # 7 days
        
        # Fetch candles from Api
        stock_data = self.api.download_data(ticker, start_date, end_date, timeframe)

        # Prepare the documents for insertion into MongoDB
        docs:List[Dict[str, Any]] = []
        datetimes_to_check = []
        for row in stock_data.iter_rows(named=True):
            curr_date = row["Date"] if row.get("Date") is not None else row.get("Datetime")
            # Prepare the document to be inserted
            candle_doc = {
                "stock_id": ObjectId(stock_id),
                "stock_name": ticker,
                "datetime": curr_date,
                "date": curr_date,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
                "timeframe": timeframe.lower()
            }
            docs.append(candle_doc)
            datetimes_to_check.append(curr_date)

        # Query the database for existing candles in bulk (by datetime and timeframe)
        existing_candles = self.dal.find({
            "stock_id": ObjectId(stock_id),
            "datetime": {"$in": datetimes_to_check},
            "timeframe": timeframe.lower()
        })

        # Create a set of tuples for existing records to check against
        existing_records = {(candle.datetime, candle.timeframe) for candle in existing_candles}

        # Filter out existing records by their unique combination of fields
        new_docs = [
            doc for doc in docs
            if (doc["datetime"], doc["timeframe"]) not in existing_records
        ]

        # Insert the new candles into the database
        if new_docs:
            print(f"Inserting {len(new_docs)} new candles for stock: {ticker}, timeframe: {timeframe}")
            self.dal.insert_many(new_docs)
        else:
            print(f"No new candles to insert for stock: {ticker}, timeframe: {timeframe}")


    def get_candles_df_by_stock_from_to(self, ticker: str,start_date: date,end_date: date, timeframe: str):
        candles = self.dal.get_candles_by_stock(ticker,start_date,end_date, timeframe)
        candles_df = []
        for candle in candles:
            candle = {
                "Datetime": candle.datetime,
                "Open": candle.open,
                "High": candle.high,
                "Low": candle.low,
                "Close": candle.close,
                "Volume": candle.volume,
                "timeframe": timeframe
                }
            candles_df.append(candle)
        return pl.DataFrame(candles_df)
    

