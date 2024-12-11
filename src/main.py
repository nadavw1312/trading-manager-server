from fastapi import FastAPI

from app import init_app
from features.big_data.backtests.polar_tests.join_vs_groupby import test_group_by_vs_join_asof
from common.middlewares.exception_middleware import ExceptionMiddleware
from common.middlewares.response_middleware import ensure_success_response_middleware
from routes import register_routes_v1
from common.services.proxy.init_proxy_locator_cs import init_proxy_locator_cs
from server.src.common.middlewares.log_request_time import log_request_time
from server.src.features.big_data.calculations.calculations_orch import CalculationsOrch
from server.src.features.big_data.candles.candles_bl import CandlesBl
from fastapi.middleware.cors import CORSMiddleware

# CandlesBl().sync_candles_for_all_stock("1d")

app = FastAPI()

init_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        reload_excludes=["venv", "__pycache__", "node_modules",".docker","tmp","logs"]
    )