from .sma_above_ema import data_dict

data_dict_v3 = data_dict.copy()
data_dict_v3['name'] = "SMA Crosses Above EMA"
data_dict_v3['symbol'] = "smaCrossesAboveEma"
data_dict_v3['class_name'] = "SmaCrossesAboveEma"
data_dict_v3['actions'] = ["crosses_above"]
data_dict_v3['short_description'] = "Checks if the Simple Moving Average (SMA) crosses above the Exponential Moving Average (EMA)."
data_dict_v3['long_description'] = "This condition evaluates whether the SMA of the 'Close' prices crosses above the EMA, often interpreted as a bullish signal indicating a potential upward trend."
data_dict_v3['trader_usage_example'] = "A trader might use this condition to enter a long position when the SMA crosses above the EMA."
data_dict_v3['programmer_usage_example'] = "SmaCrossesAboveEma['calc_pl'](dfs, {'condition_timeframe': '1d', 'is_long': True, 'sma_window': 50, 'ema_window': 20})"
data_dict_v3['canonical_form'] = "IF SMA(window=sma_window) crosses_above EMA(window=ema_window) THEN signal = True"
data_dict_v3['unique_signature'] = "<computed_hash_v3>"  # Different hash due to different canonical_form
data_dict_v3['purpose'] = "Identify bullish crossover when SMA crosses above EMA"
data_dict_v3['condition_logic'] = "SMA crosses above EMA"
data_dict_v3['actions'] = ["crosses_above"]
data_dict_v3['calc_pl'] = """
import polars as pl

def calc_pl(dfs, params):
    condition_timeframe = params['condition_timeframe']
    is_long = params['is_long']
    sma_window = params['sma_window']
    ema_window = params['ema_window']

    # Get the main DataFrame for the condition timeframe
    df = dfs[condition_timeframe]

    # Calculate SMA and EMA
    sma_params = {"timeframe": condition_timeframe, "window": sma_window}
    ema_params = {"timeframe": condition_timeframe, "window": ema_window}

    sma_result = globals().get('sma')['calc_pl'](df, sma_params)
    ema_result = globals().get('ema')['calc_pl'](df, ema_params)

    # Merge SMA and EMA results into the original DataFrame
    df = df.join(sma_result, on="Datetime", how="left").join(ema_result, on="Datetime", how="left")

    # Generate column names
    sma_col = f"SMA_{condition_timeframe}_{sma_window}"
    ema_col = f"EMA_{condition_timeframe}_{ema_window}"

    # Determine condition
    if is_long:
        condition = (
            (pl.col(sma_col).shift(1) <= pl.col(ema_col).shift(1)) &
            (pl.col(sma_col) > pl.col(ema_col))
        )
    else:
        condition = (
            (pl.col(sma_col).shift(1) >= pl.col(ema_col).shift(1)) &
            (pl.col(sma_col) < pl.col(ema_col))
        )

    # Return the condition as a Boolean Series
    return df.with_columns(condition.alias("Condition")).select("Condition")
"""
