import logging
from pymongo import MongoClient, UpdateOne
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError, BulkWriteError
from pydantic import ValidationError
from typing import  Any, Dict, Generic, Type, TypeVar, List
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference
from bson import ObjectId

from common.base.base_dal import BaseDal
from common.base.mongo_base_model import MongoBaseModel



T_Model = TypeVar('T_Model', bound=MongoBaseModel)

class BaseMongoDal(BaseDal[T_Model], Generic[T_Model]):
    """
    MongoDB-specific implementation of BaseDal.
    Enforces that T must extend MongoBaseModel.
    """
    def __init__(self, data_class: Type[T_Model], collection_name: str, db_name: str = 'stock_data'):            
        self.client: MongoClient[Any] = MongoClient('mongodb://localhost:27017')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.data_class = data_class

    def start_transaction(self) -> ClientSession:
        session = self.client.start_session()
        session.start_transaction( # type: ignore
            read_concern=ReadConcern("local"),
            write_concern=WriteConcern("majority"),
            read_preference=ReadPreference.PRIMARY
        )
        return session

    def commit_transaction(self, session: ClientSession) -> None:
        session.commit_transaction()

    def abort_transaction(self, session: ClientSession):
        session.abort_transaction()
        
    def end_session(self, session: ClientSession):
        session.end_session()

    def insert_one(self, document: dict[str, Any], session: ClientSession | None = None) -> T_Model:
        try:
            validated_document = self.data_class(**document)  # Validate with Pydantic model
            result = self.collection.insert_one(validated_document.model_dump(by_alias=True), session=session)
            validated_document.id = result.inserted_id
            return validated_document
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            print(f"Error inserting document: {e}")
            raise
    
    def insert_many(self, documents: List[dict[str, Any]], session: ClientSession | None = None) -> List[T_Model]:
        try:
            # First validate the documents without _id
            validated_models = [self.data_class(**{k: v for k, v in doc.items() if k != '_id'}) for doc in documents]
            
            # Convert to dict and let MongoDB handle _id generation
            validated_documents = [model.model_dump(by_alias=True, exclude={'id'}) for model in validated_models]
            
            # Insert documents and let MongoDB generate _ids
            result = self.collection.insert_many(validated_documents, session=session)
            
            # Update the documents with the generated _ids
            for doc, inserted_id in zip(validated_documents, result.inserted_ids):
                doc["_id"] = inserted_id
            
            return [self.data_class(**doc) for doc in validated_documents]
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            print(f"Error inserting multiple documents: {e}")
            raise
        
    def find(self, query: dict[str, Any], projection: dict[str, int] | None = None, session: ClientSession | None = None) -> List[T_Model]:
        try:
            documents = list(self.collection.find(query, projection, session=session))
            return [self.data_class(**doc) for doc in documents]
        except PyMongoError as e:
            print(f"Error finding documents: {e}")
            raise
        
    def find_all(self, session: ClientSession | None = None) -> List[T_Model]:
        try:
            documents = list(self.collection.find({}, session=session))
            result= [self.data_class(**doc) for doc in documents]
            logging.info(f"{result}")
            return result
        except PyMongoError as e:
            print(f"Error finding all documents: {e}")
            raise

    def find_one(self, query: dict[str, Any], projection: dict[str, int] | None = None, session: ClientSession | None = None) -> T_Model:
        try:
            document = self.collection.find_one(query, projection, session=session)
            if document is None:
                raise ValueError("Document not found")
            return self.data_class(**document)
        except PyMongoError as e:
            print(f"Error finding document: {e}")
            raise

    def update_one(self, query: dict[str, Any], update: dict[str, Any], session: ClientSession | None = None) -> dict[str, int]:
        try:
            validated_update = self.data_class(**update).model_dump(by_alias=True)  # Validate update document
            result = self.collection.update_one(query, {'$set': validated_update}, session=session)
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            print(f"Error updating document: {e}")
            raise

    def update_many(self, query: dict[str, Any], update: dict[str, Any], session: ClientSession | None = None) -> dict[str, int]:
        try:
            validated_update = self.data_class(**update).model_dump(by_alias=True)  # Validate update document
            result = self.collection.update_many(query, {'$set': validated_update}, session=session)
            return {"matched_count": result.matched_count, "modified_count": result.modified_count}
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            print(f"Error updating documents: {e}")
            raise
    
    def upsert(self, query: dict[str, Any], document: dict[str, Any], session: ClientSession | None = None) -> dict[str, int | str]:
        try:
            validated_document = self.data_class(**document).model_dump(by_alias=True)  # Validate document
            result = self.collection.update_one(query, {'$set': validated_document}, upsert=True, session=session)
            return {"matched_count": result.matched_count, "modified_count": result.modified_count, "upserted_id": result.upserted_id}
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            print(f"Error upserting document: {e}")
            raise

    def upsert_many(self, documents: List[dict[str, Any]], session: ClientSession | None = None) -> List[Dict[str, Any]]:
        try:
            operations: List[UpdateOne] = [
                UpdateOne({"_id": doc["_id"]}, {"$set": self.data_class(**doc).model_dump(by_alias=True)}, upsert=True) for doc in documents
            ]
            result = self.collection.bulk_write(requests=operations, session=session)# type: ignore
            return [{"matched_count": result.matched_count, "modified_count": result.modified_count, "upserted_ids": result.upserted_ids}]
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except BulkWriteError as bwe:
            print(f"Bulk write error: {bwe.details}")
            raise
        except PyMongoError as e:
            print(f"Error upserting multiple documents: {e}")
            raise

    def delete_one(self, query: dict[str, Any], session: ClientSession | None = None) -> dict[str, int]:
        try:
            result = self.collection.delete_one(query, session=session)
            return {"deleted_count": result.deleted_count}
        except PyMongoError as e:
            print(f"Error deleting document: {e}")
            raise

    def delete_many(self, query: dict[str, Any], session: ClientSession | None = None) -> dict[str, int]:
        try:
            result = self.collection.delete_many(query, session=session)
            return {"deleted_count": result.deleted_count}
        except PyMongoError as e:
            print(f"Error deleting documents: {e}")
            raise

    def count_documents(self, query: dict[str, Any], session: ClientSession | None = None) -> int:
        try:
            return self.collection.count_documents(query, session=session)
        except PyMongoError as e:
            print(f"Error counting documents: {e}")
            raise

    def aggregate(self, pipeline: List[Dict[str, Any]], session: ClientSession | None = None) -> List[Dict[str, Any]]:
        try:
            return list(self.collection.aggregate(pipeline, session=session))
        except PyMongoError as e:
            print(f"Error running aggregation: {e}")
            raise
