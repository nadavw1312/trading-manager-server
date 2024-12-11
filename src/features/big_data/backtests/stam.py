import polars as pl

from utils.timer import Timer
from datetime import datetime
from typing import Callable, Dict, List
import typing

import polars as pl

from utils.timer import Timer  # Make sure you have this Timer class defined



class BacktestEngine:
    def backtest(self, dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestCondition],
                 exit_conditions: List[BacktestCondition]) -> pl.DataFrame:
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
                primary_timeframe = entry_conditions[0].params[
                    "condition_timeframe"]  # Assuming all entry conditions use the same timeframe
                df = self._prepare_primary_dataframe(dfs, primary_timeframe)

            # Phase 2: Compute Entry Conditions and Signals
            with Timer("--------Phase 2 total --------") as t:
                df = self._compute_entry_signals_and_propagate(df, dfs, entry_conditions)

            dfs[entry_conditions[0].params["condition_timeframe"]] = df

            # Phase 3: Compute Exit Conditions and Signals
            with Timer("--------Phase 3 total --------") as t:
                df = self._compute_exit_signals(df, dfs, exit_conditions)

            # Phase 4: Compile Trades and Calculate Profit
            with Timer("--------Phase 4 total --------") as t:
                trades = self._compile_trades(df)
                total_profit = trades['profit'].sum()

        # Output results
        print(trades)
        print(f"Total Profit: {total_profit}")
        return trades

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.DataFrame], primary_timeframe: str) -> pl.DataFrame:
        """Prepare the primary timeframe DataFrame and ensure necessary columns."""
        df = dfs[primary_timeframe]
        return df

    def _compute_entry_signals_and_propagate(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],
                                             entry_conditions: List[BacktestCondition]) -> pl.DataFrame:
        """Compute entry signals, position IDs, and propagate entry data."""

        entry_signals = []
        for entry_condition in entry_conditions:
            with Timer(f"--------Phase 2 entry condition: {entry_condition.name} --------") as t:
                condition_result = entry_condition.calc(dfs, entry_condition.params)
                if not isinstance(condition_result, pl.Series):
                    raise ValueError("entry_logic_func must return a polars Series.")
                entry_signals.append(condition_result)

        # Get max_trades_per_day from parameters (default to 1 if not specified)
        max_trades_per_day = entry_conditions[0].params.get('max_trades_per_day', 1)

        # Combine entry signals
        with Timer("--------Phase 2 combine entry_signals --------") as t:
            combined_entry_signal = entry_signals[0] 
            for signal in entry_signals[1:]:
                combined_entry_signal &= signal

        # Clean the entry signals to only keep the first True in consecutive Trues
        with Timer("--------Phase 2 entry_signal --------") as t:
            entry_signal = combined_entry_signal & (~combined_entry_signal.shift(1).fill_null(False))

        # Compute cumulative position IDs based on entry signals
        with Timer("--------Phase 2 position_id --------") as t:
            position_id = entry_signal.cast(int).cum_sum().cast(pl.Int32)

        # Add entry_signal and position_id to DataFrame
        with Timer("--------Phase 2 with_columns 1 --------") as t:
            df = df.with_columns([
                entry_signal.alias('entry_signal'),
                pl.when(entry_signal)
                    .then(position_id)
                    .otherwise(None)
                    .alias('position_id').fill_null(strategy='forward')
            ])

        # Add 'daily_trade_count' column (MOVED AFTER 'entry_signal' is defined)
        with Timer("--------Phase 2 daily_trade_count --------") as t:
            df = df.with_columns([
                pl.col('entry_signal').cast(int).cum_sum().over(pl.col('Datetime').dt.date()).alias(
                    'daily_trade_count')
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

    def _compute_exit_signals(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],
                              exit_conditions: List[BacktestCondition]) -> pl.DataFrame:
        """Compute exit conditions and add signals for exiting trades."""

        exit_signals = []


        for exit_condition in exit_conditions:
            with Timer(f"--------Phase 3 exit condition: {exit_condition.name} --------") as t:
                condition_result = exit_condition.calc(dfs, exit_condition.params)
                if not isinstance(condition_result, pl.Series):
                    raise ValueError("exit_logic_func must return a polars Series for exit conditions.")
                exit_signals.append(condition_result)

        # Combine exit signals (e.g., using any() for OR, all() for AND)
        with Timer("--------Phase 3 combine exit_signals --------") as t:
            combined_exit_signal = exit_signals[0]  # Example: any condition triggers exit
            for signal in exit_signals[1:]:
                # Example: Use `|` for OR logic, or `&` for AND logic
                combined_exit_signal &= signal  # Replace `&=` with `|=` for OR logic

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

        # Add 'position_active' column initialized to False
        df = df.with_columns([pl.lit(False).alias('position_active')])
        # Update 'position_active' based on entry and exit signals
        with Timer("--------Phase 3 with_columns 3 --------") as t:
            df = df.with_columns([
                pl.when(pl.col('entry_signal'))
                    .then(True)
                    .when(pl.col('exit_signal'))
                    .then(False)
                    .otherwise(pl.col('position_active').shift(1))
                    .fill_null(False)
                    .alias('position_active')
            ])

        return df
    
    def _compile_trades(self, df: pl.DataFrame) -> pl.DataFrame:
        """Compile trades based on entry and exit signals, applying the daily trade limit."""

        # Get max_trades_per_day from parameters (default to 1 if not specified)
        max_trades_per_day = 4  # Get this from your params 

        def apply_trade_limit(group_df: pl.DataFrame) -> pl.DataFrame:
            return group_df.head(max_trades_per_day)

        with Timer("--------Phase 4 trades filter --------") as t:
            # 1. Initial Trade Compilation
            trades = (
                df.filter(pl.col('position_id').is_not_null())
                .group_by('position_id')
                .agg([
                    pl.col('Datetime').filter(pl.col('entry_signal')).first().alias('entry_time'),
                    pl.col('Datetime').filter(pl.col('exit_signal')).first().alias('exit_time'),
                    pl.col('entry_price').first().alias('entry_price'),
                    pl.col('Close').filter(pl.col('exit_signal')).first().alias('exit_price'),
                    (pl.col('Close').filter(pl.col('exit_signal')).first() - pl.col('entry_price').first()).alias('profit')
                ])
                .sort('entry_time')
                .with_columns([pl.col('entry_time').dt.date().alias('entry_date')])  # Add entry_date column
                .sort(['entry_date', 'entry_time'])  # Sort by date and time
            )

            # 2. Apply Daily Trade Limit
            trades = (
                trades
                .group_by('entry_date')
                .map_groups(apply_trade_limit)  # Use map_groups to apply the function to each group
                .sort('entry_time')  # Sort by entry_time again
            )

            # 3. Recalculate Position IDs (optional, but might be needed for consistency)
            trades = trades.with_columns([
                pl.arange(1, len(trades) + 1).alias('position_id')  # Reset position IDs
            ])

        return trades

def _compile_trades2(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Compile trades based on entry and exit signals, applying the daily trade limit 
        and considering positions that can span multiple days.
        """

        # Get parameters
        max_trades_per_day = 4  # Get this from your params
        allow_multi_day_positions = False  # Get this from your params

        def apply_trade_limit_and_filter(group_df: pl.DataFrame) -> pl.DataFrame:
            group_df = group_df.sort('entry_time')  # Sort within the group by 'entry_time'
            
            if allow_multi_day_positions:
                # If multi-day positions are allowed, filter based on completion date
                group_df = group_df.with_columns([
                    pl.col("exit_time").dt.date().alias("completion_date")
                ])
                group_df = (
                    group_df
                    .with_columns([
                        pl.arange(0, len(group_df)).alias("row_number")
                    ])
                    .with_columns([
                        pl.col("exit_time").is_not_null().cum_sum().over(pl.col("row_number")).alias("exit_time_count"),
                        pl.lit(1).cum_sum().over(pl.col("row_number")).alias("trade_count")
                    ])
                    .filter(pl.col("exit_time_count") >= pl.col("trade_count"))
                )
            else:
                # If multi-day positions are not allowed, apply trade limit and filter based on entry date
                group_df = (
                    group_df
                    .head(max_trades_per_day)  # Apply trade limit first
                    .with_columns([
                        pl.arange(0, len(group_df)).alias("row_number")
                    ])
                    .with_columns([
                        pl.col("exit_time").is_not_null().cum_sum().over(pl.col("row_number")).alias("exit_time_count"),
                        pl.lit(1).cum_sum().over(pl.col("row_number")).alias("trade_count")
                    ])
                    .filter(pl.col("exit_time_count") >= pl.col("trade_count"))
                )
            return group_df

        with Timer("--------Phase 4 trades filter --------") as t:
            # 1. Initial Trade Compilation
            trades = (
                df.filter(pl.col('position_id').is_not_null())
                .group_by('position_id')
                .agg([
                    pl.col('Datetime').filter(pl.col('entry_signal')).first().alias('entry_time'),
                    pl.col('Datetime').filter(pl.col('exit_signal')).first().alias('exit_time'),
                    pl.col('entry_price').first().alias('entry_price'),
                    pl.col('Close').filter(pl.col('exit_signal')).first().alias('exit_price'),
                    (pl.col('Close').filter(pl.col('exit_signal')).first() - pl.col('entry_price').first()).alias(
                        'profit')
                ])
                .sort('entry_time')
                .with_columns([pl.col('entry_time').dt.date().alias('entry_date')])  # Add entry_date column
                .sort(['entry_date', 'entry_time'])  # Sort by date and time
            )

                # 2. Apply Trade Limit and Filtering Logic
            if allow_multi_day_positions:
                # If multi-day positions are allowed, add 'completion_date' and group by it
                trades = (
                    trades
                    .with_columns([
                        pl.col("exit_time").dt.date().alias("completion_date")
                    ])
                    .group_by('completion_date')
                    .map_groups(apply_trade_limit_and_filter)  # Apply the combined function
                    .sort('entry_time')  # Sort by entry_time again
                )
            else:
                # If multi-day positions are not allowed, group by 'entry_date' and apply trade limit
                trades = (
                    trades
                    .group_by('entry_date')
                    .map_groups(apply_trade_limit_and_filter)  # Apply the combined function
                    .sort('entry_time')  # Sort by entry_time again
                )
            # 3. Recalculate Position IDs and Select Useful Columns
            trades = (
                trades
                .with_columns([
                    pl.arange(1, len(trades) + 1).alias('position_id')  # Reset position IDs
                ])
                .select([  # Select only the useful columns
                    'position_id', 'entry_time', 'exit_time', 'entry_price', 'exit_price', 'profit'
                ])
            )

            print(trades.head(20))  # Print the first 20 rows of the trades DataFrame

        return trades
def _compile_trades2(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Compile trades based on entry and exit signals, applying the daily trade limit 
        and considering positions that can span multiple days.
        """

        # Get parameters
        max_trades_per_day = 4  # Get this from your params
        allow_multi_day_positions = False  # Get this from your params

        def apply_trade_limit_and_filter(group_df: pl.DataFrame) -> pl.DataFrame:
            group_df = group_df.sort('entry_time')  # Sort within the group by 'entry_time'
            
            if allow_multi_day_positions:
                # If multi-day positions are allowed, filter based on completion date
                group_df = group_df.with_columns([
                    pl.col("exit_time").dt.date().alias("completion_date")
                ])
                group_df = (
                    group_df
                    .with_columns([
                        pl.arange(0, len(group_df)).alias("row_number")
                    ])
                    .with_columns([
                        pl.col("exit_time").is_not_null().cum_sum().over(pl.col("row_number")).alias("exit_time_count"),
                        pl.lit(1).cum_sum().over(pl.col("row_number")).alias("trade_count")
                    ])
                    .filter(pl.col("exit_time_count") >= pl.col("trade_count"))
                )
            else:
                # If multi-day positions are not allowed, apply trade limit and filter based on entry date
                group_df = (
                    group_df
                    .head(max_trades_per_day)  # Apply trade limit first
                    .with_columns([
                        pl.arange(0, len(group_df)).alias("row_number")
                    ])
                    .with_columns([
                        pl.col("exit_time").is_not_null().cum_sum().over(pl.col("row_number")).alias("exit_time_count"),
                        pl.lit(1).cum_sum().over(pl.col("row_number")).alias("trade_count")
                    ])
                    .filter(pl.col("exit_time_count") >= pl.col("trade_count"))
                )
            return group_df

        with Timer("--------Phase 4 trades filter --------") as t:
            # 1. Initial Trade Compilation
            trades = (
                df.filter(pl.col('position_id').is_not_null())
                .group_by('position_id')
                .agg([
                    pl.col('Datetime').filter(pl.col('entry_signal')).first().alias('entry_time'),
                    pl.col('Datetime').filter(pl.col('exit_signal')).first().alias('exit_time'),
                    pl.col('entry_price').first().alias('entry_price'),
                    pl.col('Close').filter(pl.col('exit_signal')).first().alias('exit_price'),
                    (pl.col('Close').filter(pl.col('exit_signal')).first() - pl.col('entry_price').first()).alias(
                        'profit')
                ])
                .sort('entry_time')
                .with_columns([pl.col('entry_time').dt.date().alias('entry_date')])  # Add entry_date column
                .sort(['entry_date', 'entry_time'])  # Sort by date and time
            )

                # 2. Apply Trade Limit and Filtering Logic
            if allow_multi_day_positions:
                # If multi-day positions are allowed, add 'completion_date' and group by it
                trades = (
                    trades
                    .with_columns([
                        pl.col("exit_time").dt.date().alias("completion_date")
                    ])
                    .group_by('completion_date')
                    .map_groups(apply_trade_limit_and_filter)  # Apply the combined function
                    .sort('entry_time')  # Sort by entry_time again
                )
            else:
                # If multi-day positions are not allowed, group by 'entry_date' and apply trade limit
                trades = (
                    trades
                    .group_by('entry_date')
                    .map_groups(apply_trade_limit_and_filter)  # Apply the combined function
                    .sort('entry_time')  # Sort by entry_time again
                )
            # 3. Recalculate Position IDs and Select Useful Columns
            trades = (
                trades
                .with_columns([
                    pl.arange(1, len(trades) + 1).alias('position_id')  # Reset position IDs
                ])
                .select([  # Select only the useful columns
                    'position_id', 'entry_time', 'exit_time', 'entry_price', 'exit_price', 'profit'
                ])
            )

            print(trades.head(20))  # Print the first 20 rows of the trades DataFrame

        return trades