data_dict = {
    "symbol": "sma",
    "name": "Simple Moving Average",
    "short_description": "The Simple Moving Average (SMA) calculates the average of closing prices over a specified period, helping to smooth price data and identify trends.",
    "long_description": "SMA is a widely used moving average that calculates the arithmetic mean of closing prices over a specified period. It helps smooth fluctuations in price data, providing a clearer view of the trend direction. A longer SMA period results in a smoother curve, while a shorter period is more reactive to price changes, making it suitable for different trading strategies.",
    "trader_usage_example": "A trader might use a 20-period SMA to identify trends, buying when the price crosses above it and selling when it crosses below.",
    "programmer_usage_example": "sma['calc_pl'](df, {'timeframe': '1d', 'window': 20})",
    "returns_structure_of_calc_pl": {
        "type": "pl.DataFrame",
        "columns": [
            {
                "name": "SMA_<timeframe>_<window>",
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
        "window": 20
    },
    "params_fields": {
        "timeframe": {
            "type": "str",
            "range": ["1m", "1d", "1w"],
            "title": "Timeframe",
            "description": "Primary timeframe over which SMA is calculated."
        },
        "window": {
            "type": "int",
            "range": [2, 200],
            "title": "Window Period",
            "description": "The number of periods over which the SMA is calculated."
        }
    },
    "identifiers": ["Simple Moving Average", "sma", "trend indicator"],
    "category": "trend",
    "required_libraries": ["polars"],
    "required_calculations": [],
    "plot_type": "line",
    "plot_on": "candlestick",
    "plot_data_format": {
        "time_field": "Datetime",
        "value_field": ["SMA_<timeframe>_<window>"]
    },
    "calc_pl": """
def calc_pl(df, params):
    import polars as pl
    timeframe = params.get('timeframe')
    window = params.get('window')

    sma_df = df.with_columns(
        pl.col('Close').rolling_mean(window).alias(f'SMA_{timeframe}_{window}')
    )

    return sma_df.select(['Datetime', f'SMA_{timeframe}_{window}'])
"""
}
