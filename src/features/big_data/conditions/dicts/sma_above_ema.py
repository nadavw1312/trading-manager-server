data_dict = {
    "name": "SMA Above EMA",
    "symbol": "smaAboveEma",
    "class_name": "SmaAboveEma",
    "short_description": "Checks if the Simple Moving Average (SMA) is greater than the Exponential Moving Average (EMA) over a specified timeframe.",
    "long_description": "This condition evaluates whether the SMA of the 'Close' prices exceeds the EMA. Traders often use this to identify bullish trends or entry points. It is highly configurable for various timeframes and window sizes.",
    "trader_usage_example": "A trader might use this condition to identify bullish trends when the SMA is greater than the EMA, signaling a potential buy opportunity.",
    "programmer_usage_example": "SmaAboveEma['calc_pl'](dfs, {'condition_timeframe': '1d', 'is_long': True, 'sma_window': 50, 'ema_window': 20})",
    "is_only_exit": False,
    "actions": ["greater_than"],
    "logical_operators": [],
    "params": {
        "condition_timeframe": "1d",
        "is_long": True,
        "sma_window": 50,
        "ema_window": 20
    },
    "params_fields": {
        "condition_timeframe": {
            "type": "str",
            "options": ["1m", "5m", "15m", "1h", "4h", "1d"],
            "title": "Condition Timeframe",
            "description": "The timeframe for evaluating the SMA and EMA."
        },
        "is_long": {
            "type": "boolean",
            "options": [True, False],
            "title": "Is Long",
            "description": "Indicates if the condition is for a long position."
        },
        "sma_window": {
            "type": "int",
            "range": [1, 500],
            "title": "SMA Window",
            "description": "The look-back period for calculating the SMA."
        },
        "ema_window": {
            "type": "int",
            "range": [1, 500],
            "title": "EMA Window",
            "description": "The look-back period for calculating the EMA."
        }
    },
    "identifiers": ["sma", "ema", "trend", "SMA above EMA"],
    "category": "trend",
    "required_libraries": ["polars"],
    "required_calculations": ["sma", "ema"],
    "calculations_params": {
        "sma": {
            "window": "sma_window",
            "timeframe": "condition_timeframe"
        },
        "ema": {
            "window": "ema_window",
            "timeframe": "condition_timeframe"
        }
    },
    "condition_logic": "SMA > EMA",
    "canonical_form": "IF SMA(window=sma_window) > EMA(window=ema_window) THEN signal = True",
    "unique_signature": "<computed_hash_v1>",
    "purpose": "Identify bullish trends when SMA exceeds EMA",
    "tags": ["sma", "ema", "trend", "bullish"],
    "calc_pl": """
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
        condition = pl.col(sma_col) > pl.col(ema_col)
    else:
        condition = pl.col(sma_col) < pl.col(ema_col)

    # Return the condition as a Boolean Series
    return df.with_columns(condition.alias("Condition")).select("Condition")
"""
}
