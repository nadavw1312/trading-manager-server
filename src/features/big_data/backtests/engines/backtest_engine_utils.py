import polars as pl
from typing import Any, Callable, Dict, List
import typing

from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from server.src.common.services.models.conditions_model import ConditionsModel



class BacktestEngineUtils:
    def __init__(self):
        pass
    
    @staticmethod
    def to_backtest_conditions(symbol: str,calc: Callable,params: Dict[str, Any]):
        return BacktestEngineCondition(name=symbol,calc=calc,params=params)
    
    @staticmethod
    def compute_entry_signals(dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestEngineCondition]) -> pl.Series:
        entry_signals = []
        for entry_condition in entry_conditions:
            condition_result = entry_condition.calc(dfs, entry_condition.params)
            entry_signals.append(condition_result)

        combined_entry_signal = entry_signals[0]['Condition']
        for signal in entry_signals[1:]:
            combined_entry_signal &= signal['Condition']

        return combined_entry_signal
    
    @staticmethod
    def compute_exit_signals(dfs: Dict[str, pl.DataFrame], exit_conditions: List[BacktestEngineCondition]) -> pl.Series:
        exit_signals = []
        for exit_condition in exit_conditions:
            condition_result = exit_condition.calc(dfs, exit_condition.params)
            exit_signals.append(condition_result)

        combined_exit_signal = exit_signals[0]['Condition']
        for signal in exit_signals[1:]:
            combined_exit_signal |= signal['Condition']

        return combined_exit_signal
