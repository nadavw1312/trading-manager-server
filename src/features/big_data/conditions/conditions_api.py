from common.base.base_api import BaseApi
from typing import Any, Dict, List
from server.src.common.services.models.conditions_model import ConditionsModel
from server.src.features.big_data.conditions.conditions_orch import ConditionsOrch
from server.src.common.utils.singleton import singleton

@singleton
class ConditionsApi(BaseApi[ConditionsOrch, ConditionsModel]):
    def __init__(self, enabled_routes: Dict[str, bool], dependencies: List[Any] | None = None):
        # Initialize the BaseApi with the enabled routes and dependencies (if any)
        super().__init__(ConditionsOrch(), enabled_routes=enabled_routes, dependencies=dependencies)
        self.router.get("/get_all", dependencies=dependencies)(self.get_conditions) #type:ignore
        self.router.post("/find_or_create_condition_by_input", dependencies=dependencies)(self.find_or_create_condition_by_input) #type:ignore
        
    async def get_conditions(self):
        return self.orch.find_all()
    
    async def find_or_create_condition_by_input(self, user_input: str):
        return self.orch.find_or_create_condition_by_input(user_input)
            


