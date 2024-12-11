data_dict = price_exceeds_atr_exit = {
    "name": "Price Exceeds ATR Exit",
    "symbol": "priceExceedsAtrExit",
    "short_description": "Exits a position when the price moves more than 0.7% of the daily ATR from the entry price.",
    "long_description": "This condition evaluates whether the current price has moved beyond a specified percentage (0.7%) of the Average True Range (ATR) for the day from the entry price. It is commonly used to exit trades after a significant price movement to lock in profits or limit losses.",
    "trader_usage_example": "A trader might use this condition to exit a trade when the price has moved significantly in relation to the ATR, either to secure profits or avoid further losses.",
    "programmer_usage_example": "PriceExceedsAtrExit['calc_pl'](dfs, {'condition_timeframe': '1d', 'is_long': True, 'atr_window': 14, 'atr_multiplier': 0.7})",
    "is_only_exit": True,
    "actions": ["greater_than"],
    "logical_operators": ["and", "or", "not"],
    "params": {
        "condition_timeframe": "1d",
        "is_long": True,
        "atr_window": 14,
        "atr_multiplier": 0.7
    },
    "params_fields": {
        "condition_timeframe": {
            "type": "str",
            "options": ["1m", "5m", "15m", "1h", "4h", "1d"],
            "title": "Condition Timeframe",
            "description": "The timeframe for evaluating the condition."
        },
        "is_long": {
            "type": "boolean",
            "options": [True, False],
            "title": "Is Long",
            "description": "Indicates if the condition is for a long position. If false, it evaluates for short positions."
        },
        "atr_window": {
            "type": "int",
            "range": [1, 500],
            "title": "ATR Window",
            "description": "The look-back period for calculating the ATR."
        },
        "atr_multiplier": {
            "type": "float",
            "range": [0.1, 5.0],
            "title": "ATR Multiplier",
            "description": "The percentage of the ATR used to evaluate the exit condition."
        }
    },
    "calculations_params": {
        "atr": {
            "timeframe": "1d",
            "window": "atr_window"  # Use dynamic mapping from params
        }
    },
    "identifiers": ["atr", "price movement", "exit"],
    "category": "exit",
    "required_libraries": ["polars"],
    "required_calculations": ["atr"],
    "condition_logic": "abs(price - entry_price) > atr * atr_multiplier",
    "calc_pl": """
import polars as pl

def calc_pl(dfs, params):
    try:
        # Extract parameters
        condition_timeframe = params['condition_timeframe']
        is_long = params['is_long']
        atr_window = params['atr_window']
        atr_multiplier = params['atr_multiplier']

        # Generate alias for the condition
        alias_name = f"priceExceedsAtrExit_{condition_timeframe}_atr{atr_window}_mult{atr_multiplier}"

        # Get the main DataFrame for the condition timeframe
        df = dfs[condition_timeframe]

        # Ensure the DataFrame includes the required entry columns
        if "entry_price" not in df.columns or "entry_time" not in df.columns:
            raise ValueError("The DataFrame must include 'entry_price' and 'entry_time' columns for this condition.")

        # Calculate ATR using required calculations dynamically
        atr_params = {"timeframe": condition_timeframe, "window": atr_window}
        atr_result = globals().get('atr')['calc_pl'](df, atr_params)

        # Merge ATR result into the original DataFrame
        atr_col = f"ATR_{condition_timeframe}_{atr_window}"
        df = df.join(atr_result, on="Datetime", how="left")

        # Compute the threshold for price movement based on ATR
        threshold_col = (pl.col(atr_col) * atr_multiplier).alias("atr_threshold")

        df = df.with_columns(threshold_col)

        # Calculate absolute price movement from entry price
        price_movement = (pl.col("Close") - pl.col("entry_price")).abs()
        price_condition = price_movement > pl.col("atr_threshold")

        # Add condition column with alias
        df = df.with_columns(
            price_condition.alias(f"{alias_name}_Condition")
        )

        return df.select(f"{alias_name}_Condition")

    except Exception as e:
        raise ValueError(f"Error in calculating PriceExceedsAtrExit condition: {e}")
"""
}