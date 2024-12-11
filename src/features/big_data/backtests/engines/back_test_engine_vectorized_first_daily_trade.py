from typing import Dict, List
import polars as pl
from common.utils.timer import Timer
from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from features.big_data.backtests.engines.backtest_engine_utils import BacktestEngineUtils

class BackTestEngineVectorizedFirstDailyTrade:
    def backtest(self, dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestEngineCondition],
                 exit_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """
        Backtests a trading strategy on historical data based on entry and exit conditions.
        This approach uses vectorization to find entries and exits, collecting only the first entry per day.
        """
        with Timer("--------Total total --------") as t:
            # Prepare the primary timeframe DataFrame
            primary_timeframe = entry_conditions[0].params["condition_timeframe"]
            df = self._prepare_primary_dataframe(dfs, primary_timeframe)

            # Generate entry signals and add a Date column for grouping by day
            combined_entry_signal = BacktestEngineUtils.compute_entry_signals(dfs, entry_conditions)
            df = df.with_columns([
                combined_entry_signal.alias("entry_signal"),
                pl.col("Datetime").dt.truncate("1d").alias("Date")
            ])

            # Select the first entry signal each day directly using groupby-agg
            first_entry_each_day = (
                df.filter(pl.col("entry_signal"))
                  .group_by("Date")
                  .agg([
                      pl.col("index").first().alias("first_entry_index"),
                      pl.col("Close").first().alias("entry_price"),
                      pl.col("Datetime").first().alias("entry_time")
                  ])
                  .with_row_count("position_id")
            )

            # Attach entry data to the main DataFrame
            df = df.join(first_entry_each_day, on="Date", how="left")
            dfs[primary_timeframe] = df

            # Generate exit signals
            combined_exit_signal = BacktestEngineUtils.compute_exit_signals(dfs, exit_conditions)
            combined_exit_signal = combined_exit_signal.fill_null(False)
            # Step 1: Add `exit_signal_condition` as a separate column
            df = df.with_columns(
                combined_exit_signal.cast(pl.Boolean).alias("exit_signal_condition")
            )

            # Step 2: Add the comparison as a separate column
            df = df.with_columns(
                (pl.col("index") > pl.col("first_entry_index"))
                .fill_null(False)  # Handle potential null values
                .cast(pl.Boolean)
                .alias("entry_after_exit_condition")
            )

            # Step 3: Combine the two Boolean columns into `exit_signal`
            df = df.with_columns(
                (pl.col("exit_signal_condition") & pl.col("entry_after_exit_condition"))
                .alias("exit_signal")
            )

            # Aggregate trades data with entry/exit timestamps and prices
            trades = (
                df
                  .group_by("Date")
                  .agg([
                      pl.col("index").filter(pl.col("entry_signal")).first().alias("entry_index"),
                      pl.col("index").filter(pl.col("exit_signal")).first().alias("exit_index"),
                      pl.col("Datetime").filter(pl.col("entry_signal")).first().alias("entry_time"),
                      pl.col("Datetime").filter(pl.col("exit_signal")).first().alias("exit_time"),
                      pl.col("Close").filter(pl.col("entry_signal")).first().alias("entry_price"),
                      pl.col("Close").filter(pl.col("exit_signal")).first().alias("exit_price"),
                      (pl.col("Close").filter(pl.col("exit_signal")).first() - 
                       pl.col("Close").filter(pl.col("entry_signal")).first()).alias("profit")
                  ])
                  .filter(pl.col("exit_time").is_not_null())
                  .sort("entry_time")
                  .with_row_count("position_id")
            )

            # Calculate and print total profit
            total_profit = trades["profit"].sum()
            print(trades)
            print(f"Total Profit: {total_profit}")
            return trades

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.DataFrame], primary_timeframe: str) -> pl.DataFrame:
        """Prepare the primary timeframe DataFrame."""
        return dfs[primary_timeframe]
