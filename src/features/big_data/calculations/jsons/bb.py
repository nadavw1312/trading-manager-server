data_dict = {
    "symbol": "bollinger",
    "name": "Bollinger Bands",
    "short_description": "Bollinger Bands are volatility bands placed above and below a moving average. The bands widen or narrow based on market volatility.",
    "long_description": "Bollinger Bands consist of a simple moving average (SMA) and two bands placed a certain number of standard deviations away from the SMA. The upper and lower bands expand and contract with market volatility, providing a measure of price range. When the price is near the upper band, it may indicate overbought conditions, and when near the lower band, it may indicate oversold conditions.",
    "trader_usage_example": "Traders use Bollinger Bands to identify potential reversal points or to confirm trends. For example, if the price touches the upper band, it might indicate overbought conditions, signaling a potential short entry.",
    "programmer_usage_example": "bollinger['calc_pl'](df, {'timeframe': '1d', 'window': 20, 'std_dev': 2})",
    "returns_structure_of_calc_pl": {
        "type": "pl.DataFrame",
        "columns": [
            {
                "name": "BB_Middle_<timeframe>_<window>",
                "dtype": "Float64"
            },
            {
                "name": "BB_Upper_<timeframe>_<window>_<std_dev>",
                "dtype": "Float64"
            },
            {
                "name": "BB_Lower_<timeframe>_<window>_<std_dev>",
                "dtype": "Float64"
            },
            {
                "name": "Datetime",
                "dtype": "Datetime"
            }
        ]
    },
    "params": {
        "timeframe": "1d",
        "window": 20,
        "std_dev": 2
    },
    "params_fields": {
        "timeframe": {
            "type": "str",
            "range": ["1m", "1d", "1w"],
            "title": "Timeframe",
            "description": "Primary timeframe over which Bollinger Bands are calculated."
        },
        "window": {
            "type": "int",
            "range": [2, 200],
            "title": "Window Period",
            "description": "The number of periods over which the SMA is calculated for the middle band."
        },
        "std_dev": {
            "type": "float",
            "range": [0.5, 5.0],
            "title": "Standard Deviation",
            "description": "The number of standard deviations from the SMA to calculate the upper and lower bands."
        }
    },
    "identifiers": ["Bollinger Bands", "bollinger", "volatility indicator"],
    "category": "volatility",
    "required_libraries": ["polars"],
    "required_calculations": [],
    "plot_type": "line",
    "plot_on": "candlestick",
    "plot_data_format": {
        "time_field": "Datetime",
        "value_field": [
            "BB_Middle_<timeframe>_<window>",
            "BB_Upper_<timeframe>_<window>_<std_dev>",
            "BB_Lower_<timeframe>_<window>_<std_dev>"
        ]
    },
    "calc_pl": """
def calc_pl(df, params):
    import polars as pl
    timeframe = params.get('timeframe')
    window = params.get('window')
    std_dev = params.get('std_dev')

    bb_df = df.with_columns(
        pl.col("Close").rolling_mean(window).alias(f"BB_Middle_{timeframe}_{window}")
    ).with_columns(
        pl.col("Close").rolling_std(window).alias("rolling_std")
    ).with_columns([
        (pl.col(f"BB_Middle_{timeframe}_{window}") + pl.col("rolling_std") * std_dev).alias(f"BB_Upper_{timeframe}_{window}_{std_dev}"),
        (pl.col(f"BB_Middle_{timeframe}_{window}") - pl.col("rolling_std") * std_dev).alias(f"BB_Lower_{timeframe}_{window}_{std_dev}")
    ])

    return bb_df.select(["Datetime", f"BB_Middle_{timeframe}_{window}", f"BB_Upper_{timeframe}_{window}_{std_dev}", f"BB_Lower_{timeframe}_{window}_{std_dev}"])
"""
}
