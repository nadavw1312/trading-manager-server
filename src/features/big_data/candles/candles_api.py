# stocks_api.py
from common.base.base_api import BaseApi


from typing import Any, Dict, List

from features.big_data.candles.candles_orch import CandlesOrch
from features.big_data.candles.candles_api_contract import GetCandlesByTickerFromToRequest
from server.src.common.services.models.candles_model import CandleModel
# GetCandlesByTickerFromToRequest

class CandlesApi(BaseApi[CandlesOrch, CandleModel]):
    def __init__(self, enabled_routes: Dict[str, bool], dependencies: List[Any] | None = None):
        # Initialize the BaseApi with the enabled routes and dependencies (if any)
        super().__init__(CandlesOrch(), enabled_routes=enabled_routes, dependencies=dependencies)
        self.router.post("/get_candles_by_ticker_from_to", dependencies=dependencies)(self.get_candles_by_ticker_from_to) #type:ignore


    async def get_candles_by_ticker_from_to(self, request: GetCandlesByTickerFromToRequest):
        return self.orch.get_candles_by_ticker_from_to(request.stock_name,request.from_date, request.to_date, request.timeframe, return_type="dicts")
