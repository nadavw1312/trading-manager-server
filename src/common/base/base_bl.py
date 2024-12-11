from typing import Generic, TypeVar, List, Dict, Any
from common.base.base_dal import BaseDal

T_Model = TypeVar("T_Model")
T_Dal = TypeVar("T_Dal", bound=BaseDal)

class BaseBl(Generic[T_Dal, T_Model]):
    """
    Generic Business Logic (Bl) class that can work with any Data Access Layer (Dal).
    """
    def __init__(self, dal: type[T_Dal]):
        self.dal: T_Dal = dal()

    def insert_one(self, document: Dict[str, Any]):
        return self.dal.insert_one(document)

    def insert_many(self, documents: List[Dict[str, Any]]):
        return self.dal.insert_many(documents)
    
    def find_all(self):
        return self.dal.find_all()

    def find_one(self, id:str):
        return self.dal.find_one(id)

    def update_one(self, id: str, update: Dict[str, Any]):
        return self.dal.update_one(id, update)

    def upsert(self, id: str, document: Dict[str, Any]):
        return self.dal.upsert(id, document)

    def upsert_many(self, documents: List[Dict[str, Any]]):
        return self.dal.upsert_many(documents)

    def delete_one(self, id: str):
        return self.dal.delete_one(id)
