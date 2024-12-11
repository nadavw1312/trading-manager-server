# stocks_api.py
from fastapi import Request
from features.stocks.stocks_orch import StocksOrch
from common.base.base_api import BaseApi


from typing import Dict

from server.src.common.services.models.stock_model import StockModel

class StocksApi(BaseApi[StocksOrch, StockModel]):
    def __init__(self, enabled_routes: Dict[str, bool], dependencies=None):
        # Initialize the BaseApi with the enabled routes and dependencies (if any)
        super().__init__(StocksOrch(),enabled_routes=enabled_routes, dependencies=dependencies)
        self.router.get("/get_stocks", dependencies=dependencies)(self.get_stocks) #type:ignore
        self.register_base_routes()

        
    def get_stocks(self,request: Request):
        return self.orch.get_stocks()
 