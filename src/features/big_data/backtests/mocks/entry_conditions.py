
import polars as pl
from typing import Dict
from datetime import datetime
def entry_logic_func(dfs: Dict[str, pl.DataFrame], params):
    # Extract necessary parameters
    condition_timeframe = params['condition_timeframe']
    trend_timeframe = params['trend_timeframe']
    is_long = params['is_long']
    rsi_period = params['rsi_period']
    sma_period = params['sma_period']
    rsi_threshold = params['rsi_threshold']

    # Get the primary and trend DataFrames
    df_condition = dfs[condition_timeframe]
    df_trend = dfs[trend_timeframe]

    # Calculate delta
    df_condition = df_condition.with_columns([
        pl.col('Close').diff().fill_null(0).alias('delta')
    ])

    # Calculate gain and loss using pl.when
    df_condition = df_condition.with_columns([
        pl.when(pl.col('delta') > 0)
        .then(pl.col('delta'))
        .otherwise(0)
        .alias('gain'),
        pl.when(pl.col('delta') < 0)
        .then(-pl.col('delta'))
        .otherwise(0)
        .alias('loss')
    ])

    # Calculate average gain and average loss
    df_condition = df_condition.with_columns([
        pl.col('gain').rolling_mean(window_size=rsi_period).alias('avg_gain'),
        pl.col('loss').rolling_mean(window_size=rsi_period).alias('avg_loss')
    ])

    # Handle division by zero for avg_loss
    df_condition = df_condition.with_columns([
        pl.when(pl.col('avg_loss') == 0)
        .then(0)
        .otherwise(pl.col('avg_gain') / pl.col('avg_loss'))
        .alias('rs')
    ])

    # Calculate RSI
    df_condition = df_condition.with_columns([
        (100 - (100 / (1 + pl.col('rs')))).alias('rsi')
    ])

    # Calculate SMA on the trend timeframe
    df_trend = df_trend.with_columns([
        df_trend['Close'].rolling_mean(window_size=sma_period).alias('sma_trend')
    ])

    # Perform an as-of join to match condition timeframe with trend SMA
    df_condition = df_condition.join_asof(
        df_trend.select(['Datetime', 'sma_trend']),
        on='Datetime',
        strategy='backward'
    )

    # Define entry logic based on RSI and SMA
    if is_long:
        # Long condition: RSI crosses above rsi_threshold and trend is up
        entry_conditions = (df_condition['rsi'] > rsi_threshold) & (df_condition['sma_trend'] < df_condition['Close'])
    else:
        # Short condition: RSI crosses below rsi_threshold and trend is down
        entry_conditions = (df_condition['rsi'] < rsi_threshold) & (df_condition['sma_trend'] > df_condition['Close'])

    # Return the entry conditions as a Series
    return entry_conditions

# Entry Condition Dictionary
_entry_condition = {
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
    "logic_func": entry_logic_func
}


entry_conditions = [_entry_condition]