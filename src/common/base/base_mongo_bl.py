from contextlib import contextmanager
from typing import Any, Generic, Type, TypeVar, List, Dict

from common.base.base_bl import BaseBl
from pymongo.client_session import ClientSession
from common.base.base_mongo_dal import BaseMongoDal
from common.base.mongo_base_model import MongoBaseModel

# Type variables
T_Model = TypeVar("T_Model", bound=MongoBaseModel)
T_Dal = TypeVar("T_Dal", bound=BaseMongoDal)  # Not dependent on T_Model

class BaseMongoBl(BaseBl[T_Dal, T_Model]):
    def __init__(self, data_access_layer: Type[T_Dal]):
        super().__init__(data_access_layer)
        
    @contextmanager
    def start_transaction(self):
        session = self.dal.start_transaction()
        try:
            yield session
            self.dal.commit_transaction(session=session)
        except Exception as e:
            self.dal.abort_transaction(session=session)
            print(f"Transaction aborted: {e}")
            raise
        finally:
            self.dal.end_session(session=session)

    def insert_one(self, document: Dict[str, Any], session: ClientSession | None = None) -> T_Model:
        return self.dal.insert_one(document, session=session)

    def insert_many(self, documents: List[Dict[str, Any]], session: ClientSession | None = None) -> List[T_Model]:
        return self.dal.insert_many(documents, session=session)
    
    def find_all(self, session: ClientSession | None = None) -> List[T_Model]:
        return self.dal.find_all(session=session)

    def upsert_many(self, documents: List[Dict[str, Any]], session: ClientSession | None = None) -> List[Dict[str, Any]]:
        return self.dal.upsert_many(documents, session=session)

    def aggregate(self, pipeline: List[Dict[str, Any]], session: ClientSession | None = None) -> List[Dict[str, Any]]:
        return self.dal.aggregate(pipeline, session=session)
