from .sma_above_ema import data_dict

data_dict_v2 = data_dict.copy()
data_dict_v2['name'] = "SMA Above EMA with Different Windows"
data_dict_v2['symbol'] = "smaAboveEmaDiffWindows"
data_dict_v2['class_name'] = "SmaAboveEmaDiffWindows"
data_dict_v2['params']['sma_window'] = 30
data_dict_v2['params']['ema_window'] = 15
data_dict_v2['programmer_usage_example'] = "SmaAboveEmaDiffWindows['calc_pl'](dfs, {'condition_timeframe': '1h', 'is_long': True, 'sma_window': 30, 'ema_window': 15})"
data_dict_v2['canonical_form'] = data_dict['canonical_form']  # Same logic
data_dict_v2['unique_signature'] = data_dict['unique_signature']  # Would be the same because canonical_form and parameter keys are the same
data_dict_v2['purpose'] = data_dict['purpose']  # Same purpose
