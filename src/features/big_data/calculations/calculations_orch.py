from typing import Any, List
from features.big_data.calculations.calculations_bl import CalculationsBl
import polars as pl

from common.base.base_orch import BaseOrch
from common.services.proxy.interfaces.big_data.candles_common_services_contract import CandlesCommonServicesContract
from common.services.proxy.proxy_locator_cs import ProxyLocatorCS
from common.services.proxy.interfaces.stocks_common_services_contract import StocksCommonServicesContract
from server.src.common.services.models.calculations_model import CalculationsModel
from server.src.common.utils.singleton import singleton

def create_candles_orch():
    return ProxyLocatorCS.get_by_interface(CandlesCommonServicesContract)

def create_stocks_orch():
    return ProxyLocatorCS.get_by_interface(StocksCommonServicesContract)

@singleton
class CalculationsOrch(BaseOrch[CalculationsBl, CalculationsModel]):
    def __init__(self):
        super().__init__(CalculationsBl())
        
    def get_calculations(self):
        return self.bl.get_calculations()

    def document_calculations(self):
        return self.bl.document_calculations()
    
    def add_calculation_to_df(self, df: pl.DataFrame, calculation_symbol: str, calculation_params: dict[str, Any] = {}):
        return self.bl.add_calculation_to_df(df, calculation_symbol, calculation_params)
    
    def get_calculation_by_symbol_from_to(self, calculation_symbol: str, calculation_params: dict[str, Any], from_date: str, to_date: str, stock_symbol: str) :
        candles_orch = create_candles_orch()
        stocks_orch = create_stocks_orch()
        stock = stocks_orch.get_stock_by_ticker(stock_symbol)
        if "timeframe" not in calculation_params:
            raise ValueError("timeframe is required in calculation_params")
        # Use the CandlesOrch to get the candle data
        candles_df = candles_orch.get_candles_by_ticker_from_to(stock.ticker, from_date, to_date,calculation_params["timeframe"],return_type='df')
        # Perform the calculation using the CalculationsBl
        calculation_df = self.bl.add_calculation_to_df(candles_df, calculation_symbol, calculation_params)
        # Replace NaN and null values with 0
        calculation_df = calculation_df.drop_nulls()
        
        # Convert to dictionary if needed
        return calculation_df.to_dict(as_series=False)

    def get_all_symbols(self):
        return self.bl.get_all_symbols()
