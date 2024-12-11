from typing import Any, Dict, List
from server.src.features.big_data.conditions.conditions_bl import ConditionsBl
import polars as pl

from common.base.base_orch import BaseOrch
from common.services.proxy.interfaces.big_data.candles_common_services_contract import CandlesCommonServicesContract
from common.services.proxy.proxy_locator_cs import ProxyLocatorCS
from common.services.proxy.interfaces.stocks_common_services_contract import StocksCommonServicesContract
from server.src.common.services.models.conditions_model import ConditionsModel
from server.src.common.utils.singleton import singleton
from server.src.features.big_data.conditions.condition_checker import ConditionChecker

def create_candles_orch():
    return ProxyLocatorCS.get_by_interface(CandlesCommonServicesContract)

def create_stocks_orch():
    return ProxyLocatorCS.get_by_interface(StocksCommonServicesContract)

@singleton
class ConditionsOrch(BaseOrch[ConditionsBl, ConditionsModel]):
    def __init__(self):
        super().__init__(ConditionsBl())
        
    def get_conditions(self):
        return self.bl.find_all()
    
    def get_condition_by_symbol(self, symbol: str):
        return self.bl.get_condition_by_symbol(symbol)
    
    def get_compiled_calc_pl(self, condition: ConditionsModel):
        return self.bl.get_compiled_calc_pl(condition.calc_pl, condition.symbol, condition.required_calculations)
            
    def find_similar_conditions(self, embedding, top_k=5):
        return self.bl.find_similar_conditions(embedding, top_k)


    def find_or_create_condition_by_input(self, user_input: str):
        condition_checker = ConditionChecker()
        condition = condition_checker.process_user_request(user_input)
        if condition:
            return condition
        else:
            return self.bl.generate_condition(user_input)