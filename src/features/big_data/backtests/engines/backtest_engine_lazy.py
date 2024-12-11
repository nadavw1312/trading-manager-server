import polars as pl
from typing import Callable, Dict, List


class BacktestEngineLazy:
    def backtest(self, dfs: Dict[str, pl.LazyFrame], entry_conditions: List[BacktestCondition],
                 exit_conditions: List[BacktestCondition]) -> pl.LazyFrame:
        """
        Backtests a trading strategy on historical data using lazy frames.

        Args:
            dfs: A dictionary of Polars LazyFrames, keyed by timeframe.
            entry_conditions: A list of BacktestCondition for entry logic.
            exit_conditions: A list of BacktestCondition for exit logic.

        Returns:
            A Polars LazyFrame summarizing the trades executed.
        """
        primary_timeframe = entry_conditions[0].params["condition_timeframe"]
        df = self._prepare_primary_dataframe(dfs, primary_timeframe)

        # Phase 2: Compute Entry Conditions and Signals in lazy mode
        df = self._compute_entry_signals_and_propagate(df, dfs, entry_conditions)

        # Phase 3: Compute Exit Conditions and Signals in lazy mode
        df = self._compute_exit_signals(df, dfs, exit_conditions)

        # Phase 4: Compile Trades in lazy mode
        trades = self._compile_trades(df)

        # Return lazy frame without collecting to maintain lazy execution
        return trades.collect()

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.LazyFrame], primary_timeframe: str) -> pl.LazyFrame:
        return dfs[primary_timeframe]

    def _compute_entry_signals_and_propagate(self, df: pl.LazyFrame, dfs: Dict[str, pl.LazyFrame],
                                             entry_conditions: List[BacktestCondition]) -> pl.LazyFrame:
        entry_signals = []
        for entry_condition in entry_conditions:
            # Each condition returns a lazy expression
            condition_df  = entry_condition.calc(dfs, entry_condition.params)
            # Extract `entry_signal` as an expression
            entry_signal_expr = pl.col('entry_signal')
            entry_signals.append(entry_signal_expr)

        # Combine entry signals lazily
        combined_entry_signal = entry_signals[0]
        for signal in entry_signals[1:]:
            combined_entry_signal &= signal

        # Add the combined entry signal as a new column
        df = df.with_columns([
            combined_entry_signal.alias('combined_entry_signal')
        ])

        # Clean the entry signals to keep only the first True in consecutive Trues
        df = df.with_columns([
            (pl.col('combined_entry_signal') & (~pl.col('combined_entry_signal').shift(1).fill_null(False)))
            .alias('entry_signal')
        ])

        # Add position_id lazily
        df = df.with_columns([
            pl.col('entry_signal').cast(int).cum_sum().cast(pl.Int32).alias('position_id')
        ])

        # Propagate entry data lazily
        df = df.with_columns([
            pl.when(pl.col('entry_signal')).then(pl.col('Close')).otherwise(None).alias('entry_price')
        ])

        # Forward-fill entry price over position_id in lazy mode
        df = df.with_columns([
            pl.col('entry_price').fill_null(strategy='forward').over('position_id').alias('entry_price')
        ])

        return df

    def _compute_exit_signals(self, df: pl.LazyFrame, dfs: Dict[str, pl.LazyFrame],
                              exit_conditions: List[BacktestCondition]) -> pl.LazyFrame:
        exit_signals = []
        for exit_condition in exit_conditions:
            condition_result = exit_condition.calc(dfs, exit_condition.params)
            exit_signals.append(condition_result)

        # Combine exit signals lazily and add it in `with_columns`
        combined_exit_signal = exit_signals[0]
        for signal in exit_signals[1:]:
            combined_exit_signal &= signal
        
        df = df.with_columns([
            combined_exit_signal.alias('exit_condition')
        ])

        # Ensure exit happens after entry, in lazy mode
        df = df.with_columns([
            pl.when(
                (pl.col('exit_condition')) & (pl.col('Datetime') > pl.col('Datetime').over('position_id').first())
            ).then(True).otherwise(False).alias('exit_signal')
        ])

        return df

    def _compile_trades(self, df: pl.LazyFrame) -> pl.LazyFrame:
        """Compile trades based on entry and exit signals."""

        # Initial trade compilation in lazy mode
        trades = (
            df.filter(pl.col('position_id').is_not_null())
            .group_by('position_id')
            .agg([
                pl.col('Datetime').filter(pl.col('entry_signal')).first().alias('entry_time'),
                pl.col('Datetime').filter(pl.col('exit_signal')).first().alias('exit_time'),
                pl.col('Close').filter(pl.col('entry_signal')).first().alias('entry_price'),
                pl.col('Close').filter(pl.col('exit_signal')).first().alias('exit_price'),
                (pl.col('Close').filter(pl.col('exit_signal')).first() - pl.col('entry_price').first()).alias('profit')
            ])
            .filter(pl.col('exit_time').is_not_null())
            .sort('entry_time')
        )

        # Set up position_id for trades
        trades = trades.with_columns(
            pl.arange(1, pl.count() + 1).alias('position_id')
        )

        return trades



import polars as pl
from typing import Dict, List

class BackTestEngineLoopingLazy:

    def backtest(self, dfs: Dict[str, pl.LazyFrame], entry_conditions: List[BacktestCondition],
                 exit_conditions: List[BacktestCondition]) -> pl.LazyFrame:
        """
        Backtests a trading strategy on historical data in a looping fashion using lazy frames.

        Args:
            dfs: A dictionary of Polars LazyFrames, keyed by timeframe.
            entry_conditions: A list of BacktestCondition defining entry logic.
            exit_conditions: A list of BacktestCondition defining exit logic.

        Returns:
            A Polars LazyFrame summarizing the trades executed.
        """
        primary_timeframe = entry_conditions[0].params["condition_timeframe"]
        df = self._prepare_primary_dataframe(dfs, primary_timeframe)

        # Initialize lazy expressions for position tracking
        df = df.with_columns([
            pl.lit(None).alias("entry_price"),
            pl.lit(False).alias("in_position"),
            pl.lit(False).alias("entry_signal"),
            pl.lit(False).alias("exit_signal")
        ])

        in_position = False
        entry_price = None
        trades = []

        # Iterate over the DataFrame row-by-row in a lazy fashion (looping emulation with lazy filters)
        df = df.with_columns([
            # Compute entry signals lazily
            self._apply_entry_conditions(dfs, entry_conditions).alias("entry_signal"),
            # Compute exit signals lazily
            self._apply_exit_conditions(dfs, exit_conditions).alias("exit_signal")
        ])

        # Lazy loop emulation by conditional updating of state
        df = df.with_columns([
            pl.when(pl.col("entry_signal") & ~pl.col("in_position"))
            .then(pl.col("Close"))
            .otherwise(pl.col("entry_price"))
            .alias("entry_price"),
            pl.when(pl.col("entry_signal")).then(True).otherwise(pl.col("in_position")).alias("in_position"),
            pl.when(pl.col("exit_signal") & pl.col("in_position"))
            .then(False)
            .otherwise(pl.col("in_position")).alias("in_position")
        ])

        # Compile trades in lazy mode
        trades_df = self._compile_trades(df)

        return trades_df

    def _prepare_primary_dataframe(self, dfs: Dict[str, pl.LazyFrame], primary_timeframe: str) -> pl.LazyFrame:
        return dfs[primary_timeframe]

    def _apply_entry_conditions(self, dfs: Dict[str, pl.LazyFrame], conditions: List[BacktestCondition]) -> pl.Expr:
        entry_signals = [cond.calc(dfs, cond.params) for cond in conditions]
        combined_entry_signal = entry_signals[0]
        for signal in entry_signals[1:]:
            combined_entry_signal &= signal
        return combined_entry_signal

    def _apply_exit_conditions(self, dfs: Dict[str, pl.LazyFrame], conditions: List[BacktestCondition]) -> pl.Expr:
        exit_signals = [cond.calc(dfs, cond.params) for cond in conditions]
        combined_exit_signal = exit_signals[0]
        for signal in exit_signals[1:]:
            combined_exit_signal &= signal
        return combined_exit_signal

    def _compile_trades(self, df: pl.LazyFrame) -> pl.LazyFrame:
        """Compiles trades based on entry and exit signals in lazy mode."""
        trades = (
            df.filter(pl.col("entry_signal") | pl.col("exit_signal"))
            .group_by("position_id")
            .agg([
                pl.col("Datetime").filter(pl.col("entry_signal")).first().alias("entry_time"),
                pl.col("Datetime").filter(pl.col("exit_signal")).first().alias("exit_time"),
                pl.col("entry_price").first().alias("entry_price"),
                pl.col("Close").filter(pl.col("exit_signal")).first().alias("exit_price"),
                (pl.col("Close").filter(pl.col("exit_signal")).first() - pl.col("entry_price")).alias("profit")
            ])
            .sort("entry_time")
        )
        return trades.collect()


class BackTestEngineVectorizedLazy:
    def backtest(self, dfs: Dict[str, pl.LazyFrame], entry_conditions: List[BacktestCondition],
                 exit_conditions: List[BacktestCondition]) -> pl.DataFrame:
        """
        Backtests a trading strategy on historical data based on entry and exit conditions.
        This approach uses lazy evaluation to optimize performance.
        """

        # Prepare the primary timeframe LazyFrame
        primary_timeframe = entry_conditions[0].params["condition_timeframe"]
        df = self._prepare_primary_lazyframe(dfs, primary_timeframe)

        trades = []  # To store executed trades

        # Initialize a mask for processed rows as a new column
        df = df.with_columns(pl.lit(False).alias("processed"))

        while True:
            # Compute entry and exit signals lazily
            df = self._compute_signals(df, dfs, entry_conditions, exit_conditions)
            if df is None:
                break  # No more data, end the loop

            # Apply the mask to ignore already processed rows
            unprocessed_df = df.filter(~pl.col('processed'))

            # Find first entry signal after the current point
            first_entry_idx = unprocessed_df.filter(pl.col('entry_signal')).select(pl.col('index').min()).collect().item()
            if first_entry_idx is None:
                break  # No more entries, end the loop

            # Find the corresponding exit signal after the entry
            entry_df = unprocessed_df.filter(pl.col('index') >= first_entry_idx)
            first_exit_idx = entry_df.filter(pl.col('exit_signal')).select(pl.col('index').min()).collect().item()
            if first_exit_idx is None:
                break  # No more exits, end the loop

            # Record the trade
            entry_row = df.filter(pl.col('index') == first_entry_idx).collect()
            exit_row = df.filter(pl.col('index') == first_exit_idx).collect()
            if entry_row.is_empty() or exit_row.is_empty():
                break  # No more data, end the loop

            trades.append({
                'entry_time': entry_row['Datetime'][0],
                'exit_time': exit_row['Datetime'][0],
                'entry_price': entry_row['Close'][0],
                'exit_price': exit_row['Close'][0],
                'profit': exit_row['Close'][0] - entry_row['Close'][0]
            })

            # Update the mask to mark rows before and including the first_exit_idx as processed
            df = df.with_columns(
                pl.when(pl.col('index') <= first_exit_idx)
                .then(pl.lit(True))
                .otherwise(pl.col('processed'))
                .alias('processed')
            )

            if df.is_empty():
                break  # If no rows remain, stop the loop

        # Convert trades to a Polars DataFrame
        trades_df = pl.DataFrame(trades)
        total_profit = trades_df['profit'].sum()
        print(f"Total Profit: {total_profit}")
        return trades_df

    def _prepare_primary_lazyframe(self, dfs: Dict[str, pl.LazyFrame], primary_timeframe: str) -> pl.LazyFrame:
        """Prepare the primary timeframe LazyFrame."""
        return dfs[primary_timeframe]

    def _compute_signals(self, df: pl.LazyFrame, dfs: Dict[str, pl.LazyFrame],
                         entry_conditions: List[BacktestCondition],
                         exit_conditions: List[BacktestCondition]) -> pl.LazyFrame:
        """
        Compute entry and exit signals for the entire LazyFrame at once.
        Update the `entry_price` globally for all rows when a new entry is detected.
        """

        # Initialize entry_price column
        df = df.with_columns([
            pl.lit(None).alias('entry_price'),
            pl.lit(False).alias('entry_signal'),
            pl.lit(False).alias('exit_signal')
        ])

        # Compute entry signals
        entry_signals = []
        for condition in entry_conditions:
            entry_signals.append(condition.calc(dfs, condition.params))

        # Combine all entry signals into one
        combined_entry_signal = entry_signals[0]
        for signal in entry_signals[1:]:
            combined_entry_signal &= signal

        combined_entry_signal = pl.when(~pl.col('processed')).then(combined_entry_signal).otherwise(False)

        # Add entry signal to LazyFrame
        df = df.with_columns([
            combined_entry_signal.alias('entry_signal')
        ])

        # Set entry_price globally for all rows when a new entry is detected
        first_entry_idx = df.filter(pl.col('entry_signal')).select(pl.col('index').min()).collect().item()
        if first_entry_idx is not None:
            entry_row = df.filter(pl.col('index') == first_entry_idx).collect()
            if entry_row.is_empty():
                return None
            entry_price = entry_row['Close'][0]

            # Update the entry_price column for all rows
            df = df.with_columns([
                pl.when(pl.col('entry_signal')).then(pl.lit(entry_price)).otherwise(pl.col('entry_price')).alias('entry_price')
            ])

        # Update the original LazyFrame to store entry prices
        dfs[entry_conditions[0].params["condition_timeframe"]] = df

        # Compute exit signals
        exit_signals = []
        for condition in exit_conditions:
            exit_signals.append(condition.calc(dfs, condition.params))

        # Combine all exit signals into one
        combined_exit_signal = exit_signals[0]
        for signal in exit_signals[1:]:
            combined_exit_signal &= signal

        # Add exit signals to the LazyFrame
        df = df.with_columns([
            combined_exit_signal.alias('exit_signal')
        ])

        return df
