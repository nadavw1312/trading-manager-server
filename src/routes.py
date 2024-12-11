from fastapi import FastAPI

from features.stocks.stocks_api import StocksApi
from features.big_data.calculations.calculations_api import CalculationsApi
from server.src.features.big_data.backtests.backtests_api import BacktestsApi
from server.src.features.big_data.candles.candles_api import CandlesApi
from server.src.features.big_data.conditions.conditions_api import ConditionsApi



enabled_routes = {
    "create": True,
    "get": True,
    "update": False,
    "delete": True,
}

def register_routes_v1(app: FastAPI):
    prefix = "/api/v1/"
    # Instantiate and register StocksApi with enabled routes
    stocks_api = StocksApi(enabled_routes=enabled_routes)
    app.include_router(stocks_api.router, prefix=f"{prefix}stocks", tags=["stocks"])
    calculations_api = CalculationsApi(enabled_routes=enabled_routes)
    app.include_router(calculations_api.router, prefix=f"{prefix}calculations", tags=["calculations"])
    candles_api = CandlesApi(enabled_routes=enabled_routes)
    app.include_router(candles_api.router, prefix=f"{prefix}candles", tags=["candles"])
    conditions_api = ConditionsApi(enabled_routes=enabled_routes)
    app.include_router(conditions_api.router, prefix=f"{prefix}conditions", tags=["conditions"])
    backtests_api = BacktestsApi(enabled_routes=enabled_routes)
    app.include_router(backtests_api.router, prefix=f"{prefix}backtests", tags=["backtests"])
