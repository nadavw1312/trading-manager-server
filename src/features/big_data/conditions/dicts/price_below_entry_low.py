data_dict = {
    "name": "Price Below Entry Candle Low",
    "symbol": "priceBelowEntryLow",
    "short_description": "Exits a position when the price falls below or equals the low of the entry candle.",
    "long_description": "This condition evaluates whether the current price is less than or equal to the low of the entry candle. Traders often use it as a stop-loss mechanism to protect against further losses. The condition is designed for use in either long or short positions based on the 'is_long' parameter.",
    "trader_usage_example": "A trader might use this condition to exit a trade when the price breaches the low of the entry candle, signaling a potential downtrend or increased risk.",
    "programmer_usage_example": "PriceBelowEntryLow['calc_pl'](dfs, {'condition_timeframe': '1d', 'is_long': True})",
    "is_only_exit": True,
    "actions": ["less_than_or_equal"],
    "logical_operators": ["and", "or", "not"],
    "params": {
        "condition_timeframe": "1d",
        "is_long": True
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
        }
    },
    "calculations_params": {},
    "identifiers": ["price", "entry candle low", "exit"],
    "category": "exit",
    "required_libraries": ["polars"],
    "required_calculations": [],
    "condition_logic": "price <= entry_candle_low",
    "calc_pl": """
import polars as pl

def calc_pl(dfs, params):
    try:
        # Extract parameters
        condition_timeframe = params['condition_timeframe']
        is_long = params['is_long']

        # Get the main DataFrame for the condition timeframe
        df = dfs[condition_timeframe]

        # Ensure the DataFrame contains the required columns
        if "Low" not in df.columns or "entry_price" not in df.columns or "entry_time" not in df.columns:
            raise ValueError("The DataFrame must include 'Low', 'entry_price', and 'entry_time' columns for this condition.")

        # Add a column for the entry candle low
        df = df.with_columns(
            pl.when(pl.col("Datetime") == pl.col("entry_time"))
            .then(pl.col("Low"))
            .otherwise(None)
            .alias("entry_candle_low")
        )

        # Forward-fill the entry_candle_low for the duration of the position
        df = df.with_columns(
            pl.col("entry_candle_low").fill_null(strategy="forward")
        )

        # Define the exit condition based on is_long
        if is_long:
            condition = pl.col("Low") <= pl.col("entry_candle_low")
        else:
            condition = pl.col("High") >= pl.col("entry_candle_low")  # For short positions, compare to High

        # Add the condition column
        df = df.with_columns(
            condition.alias("Condition")
        )

        # Return the condition as a Boolean Series
        return df.select("Condition")

    except Exception as e:
        raise ValueError(f"Error in calculating PriceBelowEntryLow condition: {e}")
"""
}
