from common.services.proxy.interfaces.big_data.backtests_common_services_contract import BacktestsCommonServicesContract
from common.services.proxy.interfaces.big_data.candles_common_services_contract import CandlesCommonServicesContract
from common.services.proxy.interfaces.stocks_common_services_contract import StocksCommonServicesContract
from common.services.proxy.proxy_locator_cs import ProxyLocatorCS
from features.big_data.backtests.backtests_orch import BackTestsOrch
from features.big_data.calculations.calculations_orch import CalculationsOrch
from features.big_data.candles.candles_orch import CandlesOrch
from features.big_data.conditions.conditions_orch import ConditionsOrch
from features.stocks.stocks_orch import StocksOrch


def init_proxy_locator_cs():
    # ProxyLocatorCS.register(CalculationsCommonServicesContract,CalculationsOrch())
    ProxyLocatorCS.register(StocksCommonServicesContract,StocksOrch())
    ProxyLocatorCS.register(CandlesCommonServicesContract,CandlesOrch())
    ProxyLocatorCS.register(BacktestsCommonServicesContract,BackTestsOrch())
    # ProxyLocatorCS.register(ConditionsCommonServicesContract,ConditionsOrch())