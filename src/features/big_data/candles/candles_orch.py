from typing import Any, Dict, List, Literal, Union, overload
from features.big_data.candles.candles_bl import CandlesBl
import polars as pl
from datetime import datetime

from common.base.base_orch import BaseOrch
from server.src.common.services.models.candles_model import CandleModel
from server.src.common.services.models.stock_model import StockModel
from server.src.features.stocks.stocks_orch import StocksOrch


class CandlesOrch(BaseOrch[CandlesBl, CandleModel]):
    def __init__(self):
        self.bl = CandlesBl()
        self.stocks_orch = StocksOrch()
        
        
    @overload
    def get_candles_by_ticker_from_to(
        self, 
        ticker: str, 
        from_date: str, 
        to_date: str, 
        timeframe: str, 
        return_type: Literal['dicts']
    ) -> List[Dict[str, Any]]: ...
    
    @overload
    def get_candles_by_ticker_from_to(
        self, 
        ticker: str, 
        from_date: str, 
        to_date: str, 
        timeframe: str, 
        return_type: Literal['df']
    ) -> pl.DataFrame: ...

    def get_candles_by_ticker_from_to(self, ticker: str, from_date: str, to_date: str, timeframe: str, return_type: Literal['dicts', 'df'] = 'dicts') -> Union[List[Dict], pl.DataFrame]:
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        candles_df = self.bl.get_candles_df_by_stock_from_to(ticker, start_date, end_date, timeframe)
        
        if return_type == 'dicts':
            return candles_df.to_dicts()
        elif return_type == 'df':
            return candles_df

    
    def sync_candles_for_all_timeframes(self):
        stocks = self.stocks_orch.get_stocks()
        self.bl.sync_candles_for_all_timeframes(stocks)