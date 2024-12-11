data_dict = {
    "symbol": "ema",
    "name": "Exponential Moving Average",
    "short_description": "Calculates the Exponential Moving Average (EMA) of the 'Close' prices over a specified period.",
    "long_description": "The EMA is a type of moving average that places greater weight on the most recent data points, making it more responsive to recent price changes. It is commonly used to identify trends and potential entry or exit points in trading.",
    "trader_usage_example": "A trader might use the EMA to identify bullish or bearish trends. For instance, if the price crosses above the EMA, it might indicate a potential buy signal, and if it crosses below, a sell signal.",
    "programmer_usage_example": "ema['calc_pl'](df, {'timeframe': '1d', 'window': 20})",
    "returns_structure_of_calc_pl": {
        "type": "pl.DataFrame",
        "columns": [
            {"name": "EMA_<timeframe>_<window>", "dtype": "pl.Float64"},
            {"name": "Datetime", "dtype": "pl.Datetime"}
        ]
    },
    "params": {
        "timeframe": "1d",
        "window": 20
    },
    "params_fields": {
        "timeframe": {
            "type": "str",
            "range": ["1m", "5m", "15m", "1h", "4h", "1d"],
            "title": "Timeframe",
            "description": "The primary timeframe for evaluating the EMA calculation."
        },
        "window": {
            "type": "int",
            "range": [1, 500],
            "title": "Window",
            "description": "The look-back period for calculating the EMA."
        }
    },
    "identifiers": ["ema", "exponential moving average", "trend"],
    "category": "trend",
    "required_libraries": ["polars"],
    "required_calculations": [],
    "plot_type": "line",
    "plot_on": "candlestick",
    "plot_data_format": {
        "time_field": "Datetime",
        "value_field": ["EMA_<timeframe>_<window>"]
    },
    "calc_pl": """
import polars as pl

def calc_pl(df, params):
    window = params['window']
    timeframe = params['timeframe']
    alpha = 2 / (window + 1)
    
    ema_column_name = f"EMA_{timeframe}_{window}"
    
    df = df.sort("Datetime").with_columns(
        (
            pl.col("Close")
            .ewm_mean(alpha=alpha, adjust=False, min_periods=window)
            .alias(ema_column_name)
        )
    )
    
    return df.select(["Datetime", ema_column_name])
"""
}
