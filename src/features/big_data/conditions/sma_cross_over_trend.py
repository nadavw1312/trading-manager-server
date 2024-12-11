import polars as pl

class SmaCrossOverTrend:
    @staticmethod
    def calc(dfs, params):
        df = dfs[params['condition_timeframe']]
        short_sma_window = params['short_sma_window']
        long_sma_window = params['long_sma_window']
        is_long = params['is_long']

        # Calculate short and long SMAs
        df = locals().get('Sma').calc(df, params={'timeframe': params['condition_timeframe'], 'window': short_sma_window})
        column_name = f'SMA_{params["condition_timeframe"]}_{short_sma_window}'
        df = df.with_columns(pl.col('SMA').alias(column_name))

        df = locals().get('Sma').calc(df, params={'timeframe': params['condition_timeframe'], 'window': long_sma_window})
        column_name = f'SMA_{params["condition_timeframe"]}_{long_sma_window}'
        df = df.with_columns(pl.col('SMA').alias(column_name))

        if is_long:
            return (df['Close'] > df[f'SMA_{params["condition_timeframe"]}_{short_sma_window}']) & \
                   (df[f'SMA_{params["condition_timeframe"]}_{short_sma_window}'] > df[f'SMA_{params["condition_timeframe"]}_{long_sma_window}'])
        
        return (df['Close'] < df[f'SMA_{params["condition_timeframe"]}_{short_sma_window}']) & \
               (df[f'SMA_{params["condition_timeframe"]}_{short_sma_window}'] < df[f'SMA_{params["condition_timeframe"]}_{long_sma_window}'])

