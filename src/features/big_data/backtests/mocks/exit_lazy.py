import polars as pl
from typing import Dict

def exit_logic_func_lazy(dfs: Dict[str, pl.LazyFrame], params):
    # Extract necessary parameters
    df = dfs[params['condition_timeframe']]
    atr_timeframe = params['atr_timeframe']
    is_long = params['is_long']
    atr_period = params['atr_period']
    target_atr_multiplier = params['target_atr_multiplier']
    volume_threshold = params['volume_threshold']

    # Get the ATR DataFrame in lazy mode
    df_atr = dfs[atr_timeframe]

    # Calculate True Range (TR) and ATR lazily
    tr = (pl.col('High') - pl.col('Low')).alias('tr')
    atr = tr.rolling_mean(window_size=atr_period).alias('atr_value')

    # Add the ATR to df_atr lazily
    df_atr = df_atr.with_columns(atr)

    # Perform an as-of join lazily to align ATR values with the condition timeframe
    df = df.join_asof(
        df_atr.select(['Datetime', 'atr_value']),
        on='Datetime',
        strategy='backward'
    )

    # Define the target exit price based on the entry price and ATR multiplier in lazy mode
    target_price = (
        pl.col('entry_price') + (pl.col('atr_value') * target_atr_multiplier)
        if is_long else
        pl.col('entry_price') - (pl.col('atr_value') * target_atr_multiplier)
    )

    # Define lazy exit condition based on target price and volume threshold
    exit_conditions = (
        (pl.col('Close') >= target_price) & (pl.col('Volume') >= volume_threshold)
        if is_long else
        (pl.col('Close') <= target_price) & (pl.col('Volume') >= volume_threshold)
    )

    # Attach exit conditions lazily to the DataFrame without collecting
    df = df.with_columns(exit_conditions.alias('exit_signal'))

    return df


_exit_condition_lazy = {
    "name": "ATR Target Exit with Volume Confirmation (5m and 1h)",
    "description": "Exits a position when the price moves by a multiple of ATR and the volume drops below a threshold.",
    "params": {
        "condition_timeframe": "5m",
        "atr_timeframe": "60m",
        "is_long": True,
        "atr_period": 14,
        "target_atr_multiplier": 0.2,
        "volume_threshold": 100000
    },
    "logic_func": exit_logic_func_lazy
}

exit_conditions_lazy = [_exit_condition_lazy]