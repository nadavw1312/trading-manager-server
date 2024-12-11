from typing import Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel
from common.base.base_bl import BaseBl

T_Model = TypeVar("T_Model", bound=BaseModel)
T_Bl = TypeVar("T_Bl", bound=BaseBl)  # T_Bl must be a subclass of BaseBl

class BaseOrch(Generic[T_Bl, T_Model]):
    """
    Generic Orchestrator (Orch) class that can work with current Business Logic (Bl) and other Orchestrators.
    """

    def __init__(self, bl: T_Bl):
        self.bl: T_Bl = bl

    def insert_one(self, document: Dict[str, Any]) -> T_Model:
        """
        Inserts a single document and returns the inserted model.
        """
        return self.bl.insert_one(document)

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[T_Model]:
        """
        Inserts multiple documents and returns the inserted models.
        """
        return self.bl.insert_many(documents)

    def find_all(self) -> List[T_Model]:
        """
        Finds and returns all documents.
        """
        return self.bl.find_all()

    def find_one(self, id: str) -> T_Model:
        """
        Finds a single document by ID and returns it.
        """
        return self.bl.find_one(id)

    def update_one(self, id: str, update: Dict[str, Any]) -> Dict[str, int]:
        """
        Updates a single document and returns the update result (e.g., matched and modified counts).
        """
        return self.bl.update_one(id, update)

    def upsert(self, id: str, document: Dict[str, Any]) -> Dict[str, int | str]:
        """
        Upserts a single document by ID and returns the upsert result (e.g., matched, modified, and upserted_id).
        """
        return self.bl.upsert(id, document)

    def upsert_many(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Upserts multiple documents and returns the results.
        """
        return self.bl.upsert_many(documents)

    def delete_one(self, id: str) -> Dict[str, int]:
        """
        Deletes a single document by ID and returns the delete result (e.g., deleted count).
        """
        return self.bl.delete_one(id)
