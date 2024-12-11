# base_api.py
from abc import ABC
from fastapi import  APIRouter, HTTPException
from pydantic import BaseModel
from typing import Generic, Any, List, Dict, TypeVar
from common.base.base_orch import BaseOrch

T_Orch = TypeVar('T_Orch', bound=BaseOrch)  # T_Dal must be a subclass of BaseDal
T_Model = TypeVar('T_Model', bound=BaseModel)

class BaseApi(Generic[T_Orch, T_Model],ABC):
    """
    Abstract BaseApi class that handles common logic for route registration.
    The Orchestrator layer is used to perform business logic.
    """

    def __init__(self, orch: T_Orch, enabled_routes: Dict[str, bool], dependencies: List[Any] | None = None):
        self.orch:T_Orch = orch
        self.router = APIRouter()
        self.enabled_routes = enabled_routes
        self.common_dependencies = dependencies if dependencies else []

    def register_base_routes(self):
        # Register routes based on enabled_routes configuration
        if self.enabled_routes.get("create", False):
            self.router.post("/", dependencies=self.common_dependencies)(self.create_route)

        if self.enabled_routes.get("get", False):
            self.router.get("/{item_id}", dependencies=self.common_dependencies)(self.get_route)

        if self.enabled_routes.get("update", False):
            self.router.put("/{item_id}", dependencies=self.common_dependencies)(self.update_route)

        if self.enabled_routes.get("delete", False):
            self.router.delete("/{item_id}", dependencies=self.common_dependencies)(self.delete_route)

    def create_route(self, model: BaseModel):
        """
        Route method for creating an item via the Orchestrator.
        """
        try:
            return self.orch.insert_one(model.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_route(self, item_id: str):
        """
        Route method for retrieving an item by ID via the Orchestrator.
        """
        try:
            item = self.orch.find_one(item_id)  # Assuming the Orchestrator provides this method
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_route(self, item_id: str, model: BaseModel):
        """
        Route method for updating an item by ID via the Orchestrator.
        """
        try:
            return self.orch.update_one(item_id, model.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete_route(self, item_id: str):
        """
        Route method for deleting an item by ID via the Orchestrator.
        """
        try:
            return self.orch.delete_one(item_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
