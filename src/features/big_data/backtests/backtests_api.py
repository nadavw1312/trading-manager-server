from common.base.base_api import BaseApi
from typing import Any, Dict, List
from features.big_data.backtests.backtests_orch import BackTestsOrch
from server.src.features.big_data.backtests.contracts.backtests_api_contract import BackTestCondition, BackTestPosition, BackTestRequest, BackTestResponse
from server.src.common.services.models.backtests_model import BackTestsModel

class BacktestsApi(BaseApi[BackTestsOrch, BackTestsModel]):
    def __init__(self, enabled_routes: Dict[str, bool], dependencies: List[Any] | None = None):
        # Initialize the BaseApi with the enabled routes and dependencies (if any)
        super().__init__(BackTestsOrch(), enabled_routes=enabled_routes, dependencies=dependencies)
        self.router.post("/run_example", dependencies=dependencies)(self.run_example) #type:ignore
        self.router.post("/backtest", dependencies=dependencies)(self.backtest) #type:ignore

    async def run_example(self):
        return self.orch.run_example() 
    
    async def backtest(self, request: BackTestRequest):
        entry_conditions = [BackTestCondition(symbol=condition.symbol, params=condition.params) for condition in request.entry_conditions]
        exit_conditions = [BackTestCondition(symbol=condition.symbol, params=condition.params) for condition in request.exit_conditions]
        
        raw_positions=self.orch.backtest(stocks=request.tickers, from_date=request.from_datetime, to_date=request.to_datetime,
                                entry_conditions=entry_conditions, exit_conditions=exit_conditions,
                                type=request.type)
               
        positions = {
            ticker: [
                BackTestPosition(**position) for position in positions
            ] for ticker, positions in raw_positions.items()
        }
        
        res = BackTestResponse(positions=positions)
        return res
        
