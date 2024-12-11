from server.src.features.big_data.calculations.calculations_bl import CalculationsBl
from server.src.features.big_data.candles.candles_orch import CandlesOrch


#CalculationsBl().load_and_insert_calculations()
CandlesOrch().sync_candles_for_all_timeframes()