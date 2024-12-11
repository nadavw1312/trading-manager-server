data_dict = {
    "symbol": "atr",
    "name": "Average True Range",
    "short_description": "The Average True Range (ATR) is a volatility indicator that measures the range of price movement, helping set stop levels and manage risk.",
    "long_description": "ATR is calculated as the moving average of True Range values over a specified period. True Range is the maximum of three values: high minus low, the absolute value of high minus the previous close, and the absolute value of low minus the previous close. ATR helps traders gauge market volatility, setting dynamic stop-loss levels and identifying trends. A higher ATR indicates greater volatility.",
    "trader_usage_example": "Traders use ATR to set stop-loss levels, scaling them based on current market volatility. A higher ATR might suggest larger price movements and thus wider stop levels.",
    "programmer_usage_example": "atr['calc_pl'](df, {'timeframe': '1d', 'window': 14})",
    "returns_structure_of_calc_pl": {
        "type": "pl.DataFrame",
        "columns": [
            {
                "name": "ATR_<timeframe>_<window>",
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
        "window": 14
    },
    "params_fields": {
        "timeframe": {
            "type": "str",
            "range": ["1m", "1d", "1w"],
            "title": "Timeframe",
            "description": "Primary timeframe over which ATR is evaluated."
        },
        "window": {
            "type": "int",
            "range": [2, 100],
            "title": "Window Period",
            "description": "The number of periods over which the ATR is calculated."
        }
    },
    "identifiers": ["Average True Range", "atr", "volatility indicator"],
    "category": "volatility",
    "required_libraries": ["polars"],
    "required_calculations": [],
    "plot_type": "line",
    "plot_on": "separate_pane",
    "plot_data_format": {
        "time_field": "Datetime",
        "value_field": ["ATR_<timeframe>_<window>"]
    },
    "calc_pl": """
def calc_pl(df, params):
    import polars as pl
    timeframe = params.get('timeframe')
    window = params.get('window')

    tr_df = df.with_columns([
        (pl.col("High") - pl.col("Low")).abs().alias("high_low"),
        (pl.col("High") - pl.col("Close").shift(1)).abs().alias("high_prev_close"),
        (pl.col("Low") - pl.col("Close").shift(1)).abs().alias("low_prev_close")
    ]).with_columns(
        pl.max_horizontal(["high_low", "high_prev_close", "low_prev_close"]).alias("True_Range")
    ).with_columns(
        pl.col("True_Range").rolling_mean(window).alias(f"ATR_{timeframe}_{window}")
    )

    return tr_df.select(["Datetime", f"ATR_{timeframe}_{window}"])
"""
}

