from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, List, Dict

T = TypeVar('T')  # Generic type for models

class BaseDal(ABC, Generic[T]):
    """
    Abstract Data Access Layer (Dal) class that defines the contract
    for all Dal implementations. It uses Python's abstract base class (ABC)
    to enforce method implementation.
    """
    @abstractmethod
    def insert_one(self, document: Dict[str, Any]) -> T:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[T]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def find(self, ids: List[str]) -> List[T]:
        raise NotImplementedError("This method is not implemented in the base class.")
    
    @abstractmethod
    def find_all(self) -> List[T]:
        raise NotImplementedError("This method is not implemented in the base class.")  

    @abstractmethod
    def find_one(self, id: str) -> T:
        raise NotImplementedError("This method is not implemented in the base class.")  

    @abstractmethod
    def update_one(self, id: str, update: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def update_many(self, ids: List[str], update: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def upsert(self, id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def upsert_many(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def delete_one(self, id: str) -> Dict[str, Any]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def delete_many(self, ids: List[str]) -> Dict[str, Any]:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def count_documents(self) -> int:
        raise NotImplementedError("This method is not implemented in the base class.")

    @abstractmethod
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError("This method is not implemented in the base class.")
