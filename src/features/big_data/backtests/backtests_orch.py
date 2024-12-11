
from typing import Any, Dict, List, Literal  # Import datetime

from features.big_data.backtests.engines.back_test_engine_vectorized_first_daily_trade import BackTestEngineVectorizedFirstDailyTrade
from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from features.big_data.backtests.engines.backtest_engine_vectorized_each_day import BackTestEngineVectorizedEachDay
from features.big_data.backtests.mocks import entry_conditions, entry_lazy, exit_conditions, exit_lazy
from features.big_data.backtests.backtests_bl import BackTestsBl
import polars as pl

from server.src.common.base.base_orch import BaseOrch
from server.src.common.services.models.backtests_model import BackTestsModel
from server.src.features.big_data.backtests.contracts.backtests_api_contract import BackTestCondition
from server.src.features.big_data.backtests.engines.backtest_engine_utils import BacktestEngineUtils
from server.src.features.big_data.candles.candles_orch import CandlesOrch
from server.src.features.stocks.stocks_orch import StocksOrch
from server.src.features.big_data.conditions.conditions_orch import ConditionsOrch

def create_candles_orch():
    return CandlesOrch()

def create_stocks_orch():
    return StocksOrch()

def create_conditions_orch():
    return ConditionsOrch()



class BackTestsOrch(BaseOrch[BackTestsBl, BackTestsModel]):
    def __init__(self):
        super().__init__(BackTestsBl())
        
        
    def get_timeframes_df (self,stock_symbol: str,from_date: str, to_date: str,timeframes: List[str]):
        by_timeframe_dfs = {}
        candles_orch = create_candles_orch()
        stocks_orch = create_stocks_orch()
        appl = stocks_orch.get_stock_by_ticker(stock_symbol)
        for timeframe in timeframes:
            df = candles_orch.get_candles_by_ticker_from_to(appl.ticker, from_date, to_date, timeframe,return_type='df')
            df = df.with_row_index()
            by_timeframe_dfs[timeframe] = df

        
        return by_timeframe_dfs
        
        
        
    def run_example(self):
        by_timeframe_dfs = self.get_timeframes_df('AAPL','2024-09-10','2024-10-10',['1m','5m','15m','1h','4h','1d'])

        c_condiitons = []
        e_condiitons = []
                
        c_condiitons_lazy = []
        e_condiitons_lazy = []
        
        for c in entry_conditions.entry_conditions:
            c_condiitons.append(BacktestEngineCondition(c["name"],c["params"],c["logic_func"]))
        for e in exit_conditions.exit_conditions:
            e_condiitons.append(BacktestEngineCondition(e["name"],e["params"],e["logic_func"]))
        # BackTestEngineLooping().backtest(dfs,c_condiitons,e_condiitons)
        # trades_df = BackTestEngineVectorizedEachDay().backtest(dfs1,c_condiitons,e_condiitons)
        # total_profit = trades_df['profit'].sum()
        # print(trades_df)
        # print(f"Total Profit: {total_profit}")
        BackTestEngineVectorizedFirstDailyTrade().backtest(by_timeframe_dfs,c_condiitons,e_condiitons)
        # BackTestEngineVectorizedEntryToExit().backtest(dfs2,c_condiitons,e_condiitons)
        
        for c in entry_lazy.entry_conditions_lazy:
            c_condiitons_lazy.append(BacktestEngineCondition(c["name"],c["params"],c["logic_func"]))
        for e in exit_lazy.exit_conditions_lazy:
            e_condiitons_lazy.append(BacktestEngineCondition(e["name"],e["params"],e["logic_func"]))
        
        # BacktestEngineLazy().backtest(dfs_lazy,c_condiitons_lazy,e_condiitons_lazy)
        # BackTestEngineLoopingLazy().backtest(dfs1,c_condiitons,e_condiitons)
        # print(BackTestEngineVectorizedLazy().backtest(dfs_lazy2,c_condiitons_lazy,e_condiitons_lazy))
                
        
    def backtest(self,stocks: List[str],from_date: str, to_date: str,entry_conditions: List[BackTestCondition],exit_conditions: List[BackTestCondition],type: Literal['first_daily_trade','each_day']) -> Dict[str, List[Dict[str, Any]]]:
        conditions_orch = create_conditions_orch()
        required_timeframes = {}
        backtest_entry_conditions = []
        for entry_condition in entry_conditions:
            for param in entry_condition.params:
                if 'timeframe' in param:
                    required_timeframes[entry_condition.params[param]] = None
            
            condition = conditions_orch.get_condition_by_symbol(entry_condition.symbol)
            condition.params = {**condition.params, **entry_condition.params}
            compiled_func = conditions_orch.get_compiled_calc_pl(condition)
            backtest_entry_conditions.append(BacktestEngineUtils.to_backtest_conditions(entry_condition.symbol,compiled_func['calc_pl'],entry_condition.params))
            
        backtest_exit_conditions = []
        for exit_condition in exit_conditions:
            for param in exit_condition.params:
                if 'timeframe' in param:
                    required_timeframes[exit_condition.params[param]] = None

            condition = conditions_orch.get_condition_by_symbol(exit_condition.symbol)
            condition.params = {**condition.params, **exit_condition.params}
            compiled_func = conditions_orch.get_compiled_calc_pl(condition)
            backtest_exit_conditions.append(BacktestEngineUtils.to_backtest_conditions(exit_condition.symbol,compiled_func['calc_pl'],exit_condition.params))
        
        stocks_orch = create_stocks_orch()
        positions_by_stock = {}
        for stock in stocks:
            stock_doc = stocks_orch.get_stock_by_ticker(stock)
            df = self.get_timeframes_df(stock_doc.ticker,from_date, to_date,list(required_timeframes.keys()))
            if type == 'first_daily_trade':
                positions_by_stock[stock] = BackTestEngineVectorizedFirstDailyTrade().backtest(df,backtest_entry_conditions,backtest_exit_conditions).to_dicts()
            elif type == 'each_day':
                positions_by_stock[stock] = BackTestEngineVectorizedEachDay().backtest(df,backtest_entry_conditions,backtest_exit_conditions).to_dicts()
        
        return positions_by_stock
