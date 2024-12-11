from typing import Callable, Dict, List
import polars as pl
from common.utils.timer import Timer
from features.big_data.backtests.engines.backtest_engine_models import BacktestEngineCondition
from features.big_data.backtests.engines.backtest_engine_utils import BacktestEngineUtils


class BackTestEngineLooping:

    def backtest(self, dfs: Dict[str, pl.DataFrame], entry_conditions: List[BacktestEngineCondition],
                 exit_conditions: List[BacktestEngineCondition]) -> pl.DataFrame:
        """
        Backtests a trading strategy on historical data based on entry and exit conditions.
        """

        with Timer("--------Total total --------") as t:
            # Prepare the primary timeframe DataFrame
            with Timer("--------Phase 1 total --------") as t:
                primary_timeframe = entry_conditions[0].params["condition_timeframe"]
                df = self._prepare_primary_dataframe(dfs, primary_timeframe)

                # **Add explicit index to the DataFrame**
                # df = df.with_row_count(name="index")

            # Initialize variables to control the entry-exit cycle
            in_position = False  # To track if we are in a position (after an entry)
            entry_price = None
            entry_time = None
            trades = []  # List to store executed trades
            updated_rows = []  # List to store updated rows for the DataFrame

            # Iterate through the rows using a loop (row by row)
            for i, row in enumerate(df.iter_rows(named=True)):
                updated_row = row.copy()  # Create a copy of the row for modifications

                # Check for entry if not in a position
                if not in_position:
                    entry_signal = self._check_conditions(row["index"], df, dfs, entry_conditions)
                    if entry_signal:
                        entry_price = row['Close']
                        entry_time = row['Datetime']
                        updated_row['entry_price'] = entry_price  # Set entry price for this row
                        in_position = True  # We are now in a position
                    else:
                        updated_row['entry_price'] = None  # No entry, so no entry price

                # If in a position, propagate the entry price until an exit is found
                elif in_position:
                    df = df.with_columns(pl.lit(entry_price).alias("entry_price"))
                    dfs[entry_conditions[0].params["condition_timeframe"]] = df

                    exit_signal = self._check_conditions(row["index"], df, dfs, exit_conditions)

                    if exit_signal:
                        exit_price = row['Close']
                        exit_time = row['Datetime']

                        # Record the trade
                        trades.append({
                            'entry_time': entry_time,
                            'exit_time': exit_time,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit': exit_price - entry_price
                        })

                        # Reset for the next trade
                        in_position = False
                        entry_price = None
                        entry_time = None
                        df = df.with_columns(pl.lit(entry_price).alias("entry_price"))
                        dfs[entry_conditions[0].params["condition_timeframe"]] = df

                updated_rows.append(updated_row)

            # Convert the trade list to a Polars DataFrame
            trades_df = pl.DataFrame(trades)

        total_profit = trades_df['profit'].sum()
        print(trades_df)
        print(f"Total Profit: {total_profit}")
        return trades_df

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.DataFrame], primary_timeframe: str) -> pl.DataFrame:
        """Prepare the primary timeframe DataFrame."""
        return dfs[primary_timeframe]

    def _check_conditions(self, idx: int, df: pl.DataFrame, dfs: Dict[str, pl.DataFrame],
                          conditions: List[BacktestEngineCondition]) -> bool:
        """
        Helper function to check if all conditions are met.
        `idx` is the index of the current row.
        Returns True if conditions are met, False otherwise.
        """
        for condition in conditions:
            condition_result = condition.calc(dfs, condition.params)
            # Check the condition result for the specific row index
            if not condition_result[idx]:  # Checking condition result at row 'idx'
                return False
        return True