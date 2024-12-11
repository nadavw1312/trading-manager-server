from typing import  Dict, List
import polars as pl
from common.utils.timer import Timer
from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from features.big_data.backtests.engines.backtest_engine_utils import BacktestEngineUtils

class BackTestEngineVectorizedEachDay:
    def backtest(self, dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestEngineCondition],
                 exit_conditions: List[BacktestEngineCondition], max_trades_per_day: int = 1) -> pl.DataFrame:
        """
        Backtests a trading strategy on historical data.

        Args:
            dfs: A dictionary of Polars DataFrames, keyed by timeframe.
            entry_conditions: A list of BacktestCondition, each defining an entry condition.
            exit_conditions: A list of BacktestCondition, each defining an exit condition.

        Returns:
            A Polars DataFrame summarizing the trades executed.
        """
        with Timer("--------Total total --------") as t:
            # Phase 1: Prepare the primary timeframe DataFrame
            with Timer("--------Phase 1 total --------") as t:
                primary_timeframe = entry_conditions[0].params["condition_timeframe"]  
                df = self._prepare_primary_dataframe(dfs, primary_timeframe)
                # df = df.with_row_count("index")

            # Phase 2: Compute Entry Conditions and Signals
            with Timer("--------Phase 2 total --------") as t:
                df = self._add_entry_signal(df, dfs, entry_conditions)
                df = self._add_position_id_and_entry_price(df)

            dfs[entry_conditions[0].params["condition_timeframe"]] = df

            # Phase 3: Compute Exit Conditions and Signals
            with Timer("--------Phase 3 total --------") as t:
                df = self._compute_exit_signals(df, dfs, exit_conditions)

            # Phase 4: Compile Trades and Calculate Profit
            with Timer("--------Phase 4 total --------") as t:
                trades = self._compile_trades(df, max_trades_per_day)

        return trades
    
    #region prepare primary dataframe
    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.DataFrame], primary_timeframe: str) -> pl.DataFrame:
        """Prepare the primary timeframe DataFrame and ensure necessary columns."""
        df = dfs[primary_timeframe]
        return df
    #endregion


    #region compute entry signals and propagate Phase 2
    def _add_entry_signal(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],entry_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """Create entry signals."""
        # Combine entry signals
        with Timer("-------- compute_entry_signals --------") as t:
            combined_entry_signal = BacktestEngineUtils.compute_entry_signals(dfs, entry_conditions)
            df = df.with_columns([
                combined_entry_signal.alias('combined_entry_signal')
            ])

        # Clean the entry signals to only keep the first True in consecutive Trues
        with Timer("--------Phase 2 entry_signal --------") as t:
            df = df.with_columns([
                (pl.col('combined_entry_signal') & (~pl.col('combined_entry_signal').shift(1).fill_null(False)))
                .over(pl.col('Datetime').dt.truncate('1d'))  # Ensure it works per day
                .alias('entry_signal')
            ])
        return df
    
    def _add_position_id_and_entry_price(self, df: pl.DataFrame) -> pl.DataFrame:
        """Compute position IDs based on entry signals."""
        entry_signal = df['entry_signal']
        # Compute cumulative position IDs based on entry signals
        with Timer("--------entry_signal cum_sum --------") as t:
            df = df.with_columns([
                pl.col('entry_signal').cast(int).cum_sum().cast(pl.Int32).alias('position_id')
            ])
            
        with Timer("--------entry_price fill_null --------") as t:
            df = df.with_columns([
            pl.when(pl.col('entry_signal')).then(pl.col('Close')).otherwise(None).alias('entry_price')
        ])

            df = df.with_columns([
                pl.col('entry_price').fill_null(strategy='forward').over('position_id').alias('entry_price')
            ])
        
        return df

    def _compute_entry_signals_and_propagate(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],
                                             entry_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """Compute entry signals, position IDs, and propagate entry data."""
 
        entry_signal = df['entry_signal']
        # Compute cumulative position IDs based on entry signals
        with Timer("--------Phase 2 position_id --------") as t:
            position_id = entry_signal.cast(int).cum_sum().cast(pl.Int32)

        # Add entry_signal and position_id to DataFrame
        with Timer("--------Phase 2 with_columns 1 --------") as t:
            df = df.with_columns([
                pl.when(entry_signal)
                    .then(position_id)
                    .otherwise(None)
                    .alias('position_id').fill_null(strategy='forward')
            ])

        # Propagate Entry Data (entry_price)
        with Timer("--------Phase 2 with_columns 3 --------") as t:
            df = df.with_columns([
                pl.when(pl.col('entry_signal'))
                    .then(pl.col('Close'))
                    .otherwise(None)
                    .alias('entry_price')
            ])

        with Timer("--------Phase 2 with_columns 4 --------") as t:
            df = df.with_columns([
                pl.col('entry_price').fill_null(strategy='forward').over('position_id').alias('entry_price')
            ])

        return df
    #endregion


    #region compute exit signals Phase 3
    def _compute_exit_signals(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],
                              exit_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """Compute exit conditions and add signals for exiting trades."""

        combined_exit_signal = BacktestEngineUtils.compute_exit_signals(dfs, exit_conditions)

        # Add exit_condition and target_price to DataFrame
        with Timer("--------Phase 3 with_columns 1 --------") as t:
            df = df.with_columns([
                combined_exit_signal.alias('exit_condition'),
            ])

        # Ensure exit happens after entry
        with Timer("--------Phase 3 with_columns 2 --------") as t:
            df = df.with_columns([
                pl.when(
                    (pl.col('exit_condition')) & (pl.col('Datetime') > pl.col('Datetime').over('position_id').first())
                ).then(True).otherwise(False).alias('exit_signal')
            ])

        return df
    #endregion


    #region compile trades Phase 4
    def filter_overlapping_trades(self,trades: pl.DataFrame) -> pl.DataFrame:
        """Filter out trades that start before the previous one finishes."""
        # Sort trades by entry_time
        trades = trades.sort('entry_time')

        # Create a mask to identify overlapping trades using 'exit_price'
        mask = trades['exit_price'].shift(1).is_not_null()

        # Filter out overlapping trades using the mask
        return trades.filter(mask)


    def _compile_trades(self, df: pl.DataFrame, max_trades_per_day: int = 1) -> pl.DataFrame:
        """Compile trades based on entry and exit signals"""

        with Timer("--------Phase 4 trades filter --------") as t:
            # 1. Initial Trade Compilation
            trades = (
                df.filter(pl.col('position_id').is_not_null())
                .group_by('position_id')
                .agg([
                    pl.col("index").filter(pl.col("entry_signal")).first().alias("entry_index"),
                    pl.col("index").filter(pl.col("exit_signal")).first().alias("exit_index"),
                    pl.col('Datetime').filter(pl.col('entry_signal')).first().alias('entry_time'),
                    pl.col('Datetime').filter(pl.col('exit_signal')).first().alias('exit_time'),
                    pl.col('Close').filter(pl.col('entry_signal')).first().alias('entry_price'),
                    pl.col('Close').filter(pl.col('exit_signal')).first().alias('exit_price'),
                    (pl.col('Close').filter(pl.col('exit_signal')).first() - pl.col('entry_price').first()).alias('profit')
                ]).filter(pl.col('exit_time').is_not_null())
                .sort('entry_time')
            )
            
            # Step 2: Add cumulative count per day to limit trades per day
            trades = trades.with_columns([
                pl.col('entry_time').dt.date().alias('entry_date'),  # Add entry_date column
            ])
            
            trades = trades.with_columns([
                pl.col('entry_time').cum_count().over("entry_date").alias("daily_trade_count")
            ]).sort(['entry_date', 'entry_time'])

            # Step 3: Filter to keep only the first `max_trades_per_day` trades per day
            trades = trades.filter(pl.col("daily_trade_count") <= max_trades_per_day)
            

            # # 4. Recalculate Position IDs (optional, but might be needed for consistency)
            # trades = trades.with_columns([
            #     pl.arange(1, len(trades) + 1).alias('position_id')  # Reset position IDs
            # ])

        return trades
    #endregion
