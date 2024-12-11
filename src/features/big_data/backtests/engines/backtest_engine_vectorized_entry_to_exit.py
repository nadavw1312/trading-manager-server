from typing import Callable, Dict, List
import polars as pl
from common.utils.timer import Timer
from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from features.big_data.backtests.engines.backtest_engine_utils import BacktestEngineUtils

class BackTestEngineVectorizedEntryToExit:
    def backtest(self, dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestEngineCondition],
                    exit_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """
        Backtests a trading strategy on historical data based on entry and exit conditions.
        This approach uses vectorization to find entries and exits.
        Each iteration of the loop processes the entire DataFrame, ignoring already processed rows.
        """
        with Timer("--------Total total --------") as t:
            # Prepare the primary timeframe DataFrame
            with Timer("--------Phase 1 total --------") as t:
                primary_timeframe = entry_conditions[0].params["condition_timeframe"]
                df = self._prepare_primary_dataframe(dfs, primary_timeframe)

            trades = []  # To store executed trades
            # Initialize a mask for processed rows as a new column
            df = df.with_columns(pl.lit(False).alias("processed"))

            first_combined_entry_signal = None

            while True:
                # **Compute entry and exit signals for the entire DataFrame, ignoring already processed rows**
                with Timer("----------------------create_entry_signals----------------------") as t:
                    # Check if the first combined entry signal has been computed
                    if first_combined_entry_signal is None:
                        combined_entry_signal = BacktestEngineUtils.compute_entry_signals(dfs, entry_conditions)
                        first_combined_entry_signal = combined_entry_signal
                    else:
                        combined_entry_signal = first_combined_entry_signal
                    
                    # Filter unprocessed entries only
                    df = self._create_entry_signals_to_unprocessed_df(df, combined_entry_signal)
                if df is None:
                    break  

                # Update the original DataFrame to store entry prices
                dfs[entry_conditions[0].params["condition_timeframe"]] = df

                with Timer("----------------------create_exit_signals----------------------") as t:
                    df = self._create_exit_signals(df, dfs, exit_conditions)

                # Apply the mask to ignore already processed rows
                entry_signal_series = df['entry_signal']
                exit_signal_series = df['exit_signal']
                index_series = df['index']
                processed_series = df['processed']

                with Timer("----------------------each iteration time left-----------------------") as t:
                    # Filter for unprocessed rows
                    unprocessed_mask = ~processed_series
                    unprocessed_entry_mask = unprocessed_mask & entry_signal_series
                    unprocessed_entry_indices = index_series.filter(unprocessed_entry_mask)

                    if unprocessed_entry_indices.is_empty():
                        break  # No more entries, end the loop

                    first_entry_idx = unprocessed_entry_indices.min()
                    # Find the corresponding exit signal after the entry
                    unprocessed_exit_mask = (index_series >= first_entry_idx) & unprocessed_mask & exit_signal_series
                    unprocessed_exit_indices = index_series.filter(unprocessed_exit_mask)

                    if unprocessed_exit_indices.is_empty():
                        break  # No more exits, end the loop

                    first_exit_idx = unprocessed_exit_indices.min()
                    entry_row = df.filter(pl.col('index') == first_entry_idx)
                    exit_row = df.filter(pl.col('index') == first_exit_idx)

                    if entry_row.is_empty() or exit_row.is_empty():
                        break  # No more data, end the loop

                    with Timer("--------trades.append--------") as t:
                        trades.append({
                            'entry_time': entry_row['Datetime'][0],
                            'exit_time': exit_row['Datetime'][0],
                            'entry_price': entry_row['Close'][0],
                            'exit_price': exit_row['Close'][0],
                            'profit': exit_row['Close'][0] - entry_row['Close'][0]
                        })

                    # Update the 'processed' Series
                    processed_update_mask = (index_series <= first_exit_idx)
                    processed_series = processed_series | processed_update_mask  # Mark indices as processed
                    df = df.with_columns(pl.lit(processed_series).alias("processed"))

                    if df.is_empty():
                        break  # If no rows remain, stop the loop

            # Convert trades to a Polars DataFrame
            trades_df = pl.DataFrame(trades)
            total_profit = trades_df['profit'].sum()
            print(trades_df)
            print(f"Total Profit: {total_profit}")
            return trades_df

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.DataFrame], primary_timeframe: str) -> pl.DataFrame:
        """Prepare the primary timeframe DataFrame."""
        return dfs[primary_timeframe]
    
    def _fill_entry_price_for_all_rows(self, df: pl.DataFrame) -> pl.DataFrame:
        """Initialize entry_price column and set entry price for all rows when a new entry is detected."""
        # Initialize entry_price column
        df = df.with_columns(pl.lit(None).alias('entry_price'))

        # Find the first entry signal index and set entry price
        first_entry_idx = df.filter(pl.col('entry_signal')).select('index').min()
        if first_entry_idx is not None:
            entry_row = df.filter(pl.col('index') == first_entry_idx)
            entry_price = entry_row['Close'][0]

            # Update entry price for all rows when a new entry is detected
            df = df.with_columns([
                pl.when(pl.col('entry_signal')).then(pl.lit(entry_price)).otherwise(pl.col('entry_price')).alias('entry_price')
            ])
        return df
    
    def _create_entry_signals_to_unprocessed_df(self, df: pl.DataFrame, combined_entry_signal) -> pl.DataFrame:
        """Compute entry signals for unprocessed rows and add entry_signal column."""
        combined_entry_signal = pl.when(~pl.col('processed')).then(combined_entry_signal).otherwise(False)
        df = df.with_columns([combined_entry_signal.alias('entry_signal')])
        df = self._fill_entry_price_for_all_rows(df)
        return df
    
    def _create_exit_signals(self, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame], exit_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """Compute exit signals and add exit_signal column."""
        combined_exit_signal = BacktestEngineUtils.compute_exit_signals(dfs, exit_conditions)
        df = df.with_columns([combined_exit_signal.alias('exit_signal')])
        return df
