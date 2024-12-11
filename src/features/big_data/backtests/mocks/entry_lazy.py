import polars as pl
from typing import Dict

def compute_rsi(df: pl.LazyFrame, period: int) -> pl.LazyFrame:
    # Calculate delta, gains, losses, and average gains/losses, then RSI
    df = df.with_columns(
        pl.col('Close').diff().fill_null(0).alias('delta')
    ).with_columns([
        pl.when(pl.col('delta') > 0).then(pl.col('delta')).otherwise(0).alias('gain'),
        pl.when(pl.col('delta') < 0).then(-pl.col('delta')).otherwise(0).alias('loss')
    ]).with_columns([
        pl.col('gain').rolling_mean(window_size=period).alias('avg_gain'),
        pl.col('loss').rolling_mean(window_size=period).alias('avg_loss')
    ]).with_columns([
        pl.when(pl.col('avg_loss') == 0)
        .then(0)
        .otherwise(pl.col('avg_gain') / pl.col('avg_loss'))
        .alias('rs')
    ]).with_columns([
        (100 - (100 / (1 + pl.col('rs')))).alias('rsi')
    ])
    return df

def entry_lazy_logic_func(dfs: Dict[str, pl.LazyFrame], params) -> pl.LazyFrame:
    # Extract necessary parameters
    condition_timeframe = params['condition_timeframe']
    trend_timeframe = params['trend_timeframe']
    is_long = params['is_long']
    rsi_threshold = params['rsi_threshold']

    # Access precomputed DataFrames
    df_condition = dfs[condition_timeframe]
    df_trend = dfs[trend_timeframe]

    # Ensure the RSI is computed in `df_condition` by calling `compute_rsi`
    df_condition = compute_rsi(df_condition, params['rsi_period']).collect().lazy()

    # Calculate SMA on the trend timeframe, using lazy mode
    df_trend = df_trend.with_columns(
        pl.col('Close').rolling_mean(window_size=params['sma_period']).alias('sma_trend')
    )

    # Perform an as-of join to align SMA trend with condition timeframe
    df_condition = df_condition.join_asof(
        df_trend.select(['Datetime', 'sma_trend']),
        on='Datetime',
        strategy='backward'
    )

    # Define the entry condition expression
    entry_conditions = (
        (pl.col('rsi') > rsi_threshold) & (pl.col('sma_trend') < pl.col('Close'))
        if is_long else
        (pl.col('rsi') < rsi_threshold) & (pl.col('sma_trend') > pl.col('Close'))
    )
    # Add entry conditions to the DataFrame as a new column
    df_condition = df_condition.with_columns(entry_conditions.alias('entry_signal'))

    # Return the LazyFrame with all necessary columns
    return df_condition

# Example condition setup
_entry_condition_lazy = {
    "name": "RSI Crossover with Trend Confirmation (5m and 1h)",
    "description": "Enters a position when the RSI crosses a threshold on the 5m timeframe while confirming the trend direction with the SMA on the 1h timeframe.",
    "params": {
        "condition_timeframe": "5m",
        "trend_timeframe": "60m",
        "is_long": True,
        "rsi_period": 14,
        "sma_period": 20,
        "rsi_threshold": 30
    },
    "logic_func": entry_lazy_logic_func
}

# Entry conditions as expressions
entry_conditions_lazy = [_entry_condition_lazy]
