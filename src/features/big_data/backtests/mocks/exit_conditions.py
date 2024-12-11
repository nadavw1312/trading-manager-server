
from typing import Dict
from matplotlib.pyplot import plot
import polars as pl
def exit_logic_func(dfs: Dict[str, pl.DataFrame], params):
    # Extract necessary parameters
    df = dfs[params['condition_timeframe']]
    atr_timeframe = params['atr_timeframe']
    is_long = params['is_long']
    atr_period = params['atr_period']
    target_atr_multiplier = params['target_atr_multiplier']
    volume_threshold = params['volume_threshold']

    # Get the ATR DataFrame
    df_atr = dfs[atr_timeframe]

    # Calculate True Range (TR)
    tr = df_atr['High'] - df_atr['Low']
    atr = tr.rolling_mean(window_size=atr_period).alias('atr_value')
    df_atr = df_atr.with_columns([atr])

    # Perform an as-of join to match condition timeframe with ATR
    df = df.join_asof(
        df_atr.select(['Datetime', 'atr_value']),
        on='Datetime',
        strategy='backward'
    )

    # Calculate the target exit price based on the entry price and ATR multiplier
    if is_long:
        target_price = df['entry_price'] + (df['atr_value'] * target_atr_multiplier)
        exit_conditions = df['Close'] >= target_price
    else:
        target_price = df['entry_price'] - (df['atr_value'] * target_atr_multiplier)
        exit_conditions = df['Close'] <= target_price

    return exit_conditions

# Exit Condition Dictionary
_exit_condition = {
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
    "logic_func": exit_logic_func
}

exit_conditions = [_exit_condition]