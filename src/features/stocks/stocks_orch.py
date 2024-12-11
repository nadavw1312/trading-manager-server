# stocks_orch.py


from server.src.features.stocks.stocks_bl import StocksBl
from server.src.common.base.base_orch import BaseOrch
from server.src.common.services.models.stock_model import StockModel


class StocksOrch(BaseOrch[StocksBl, StockModel]):
    def __init__(self):
        super().__init__(StocksBl())
    
    def get_stock_by_ticker(self, ticker: str) -> StockModel:
        """
        Retrieve stock by its ticker symbol.
        """
        stock = self.bl.get_stock_by_ticker(ticker)
        if not stock:
            raise ValueError(f"Stock with ticker '{ticker}' not found.")
        return stock
    
    def add_stock_if_not_exists(self, ticker: str, company_name: str = ""):
        """
        Add a stock to the database if it does not already exist.
        """
        stock_id = self.bl.add_stock_if_not_exists(ticker, company_name)
        return {"stock_id": stock_id, "message": f"Stock '{ticker}' added or already exists."}
    
    def get_stocks(self):
        return self.bl.get_stocks()
