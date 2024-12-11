from datetime import datetime

from server.src.features.stocks.stocks import NASDAQ_STOCKS
from server.src.features.stocks.stocks_dal import StocksDal
from server.src.common.base.base_mongo_bl import BaseMongoBl
from server.src.common.third_party_api.yahoo_finance_api import YahooFinanceApi

import yfinance as yf

from server.src.common.services.models.stock_model import StockModel
from server.src.common.utils.singleton import singleton


@singleton
class StocksBl(BaseMongoBl[StocksDal, StockModel]):
    def __init__(self):
        super().__init__(StocksDal)  # Dal instance for database operations
        
    def inset_all(self):
        # Fetch stock data for the top 40 Nasdaq stocks
        stocks = YahooFinanceApi().get_stocks_metadata(stock_names=NASDAQ_STOCKS)
        self.dal.insert_many(stocks)
            

    def add_stock_if_not_exists(self, ticker: str, company_name: str = "") -> str:
        """
        Add a stock if it doesn't already exist, and return the stock ID.
        """
        stock = self.dal.get_stock_by_ticker(ticker)
        if not stock:
            stock_data = {
                "ticker": ticker,
                "name": company_name,  # Use ticker if company_name is not provided
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            result = self.dal.insert_one(stock_data)
            return str(result.id)
        else:
            return str(stock.id)

    
    def get_stock_by_ticker(self, ticker: str):
        """
        Retrieves a stock by its ticker symbol.
        Returns a Stock object.
        """
        return self.dal.get_stock_by_ticker(ticker)
    
    def get_stocks(self):
        return self.dal.find({})