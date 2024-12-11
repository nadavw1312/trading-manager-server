# stocks_api.py
from common.base.base_api import BaseApi
from typing import Any, Dict, List
from features.big_data.calculations.calculations_orch import CalculationsOrch
from features.big_data.calculations.calculations_api_contract import GetCalculationBySymbolFromToRequest
from server.src.common.services.models.calculations_model import CalculationsModel
from server.src.common.utils.singleton import singleton

@singleton
class CalculationsApi(BaseApi[CalculationsOrch, CalculationsModel]):
    def __init__(self, enabled_routes: Dict[str, bool], dependencies: List[Any] | None = None):
        # Initialize the BaseApi with the enabled routes and dependencies (if any)
        super().__init__(CalculationsOrch(), enabled_routes=enabled_routes, dependencies=dependencies)
        self.router.get("/get_all", dependencies=dependencies)(self.get_calculations) #type:ignore
        self.router.post("/get_calculation_by_symbol_from_to", dependencies=dependencies)(self.get_calculation_by_symbol_from_to) #type:ignore

    async def get_calculations(self):
        return self.orch.get_calculations()

    
    async def get_calculation_by_symbol_from_to(self, request: GetCalculationBySymbolFromToRequest):
        return self.orch.get_calculation_by_symbol_from_to(request.calculation_symbol,request.calculation_params ,request.from_date, request.to_date, request.stock_symbol)
