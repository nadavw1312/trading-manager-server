from typing import Any, Callable, Dict

from server.src.features.big_data.candles.candles_orch import CandlesOrch


def validate_generated_script(script: Callable,params: Dict[str, Any]):
    candles_orch = CandlesOrch()
    candles = candles_orch.get_candles_by_ticker_from_to("5m", "TSLA", "2024-10-22", "2024-11-22",return_type='df')
    timeframe_dfs = {'5m': candles}
    try:
        script(timeframe_dfs,params)
    except Exception as e:
        print(e)
        return False
    