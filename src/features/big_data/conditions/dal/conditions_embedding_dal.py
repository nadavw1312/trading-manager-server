import json
from typing import List
from pymilvus import (
    SearchFuture,
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection, utility,MilvusClient,utility
)
from sentence_transformers import SentenceTransformer


from server.src.common.config import MILVUS_DATABASE_HOST, MILVUS_DATABASE_PORT, MILVUS_DATABASE_NAME
from server.src.common.utils.singleton import singleton
from server.src.features.big_data.conditions.dal.conditions_embedding_dal_models import ConditionEmbeddingDict

collection_name = 'condition_embeddings'

@singleton
class ConditionsEmbeddingDal():
    def __init__(self):
        self.mode = SentenceTransformer('all-MiniLM-L6-v2')
        connections.connect(host=MILVUS_DATABASE_HOST, port=MILVUS_DATABASE_PORT,db_name=MILVUS_DATABASE_NAME)
        # Check if the collection already exists
        if not connections.has_connection("collection_name"):
            # Define the fields for the collection
            fields = [
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='condition_id', dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name='condition_symbol', dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name='embedding_name', dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name='embedding_short_description', dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name='embedding_long_description', dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name='embedding_calc_pl', dtype=DataType.FLOAT_VECTOR, dim=384)
            ]
            schema = CollectionSchema(fields=fields, description='Condition Embeddings')
            self.collection = Collection(name=collection_name, schema=schema)
        else:
            self.collection = Collection(name=collection_name)
        
        # Create an index on the embedding field if it doesn't exist
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        if not self.collection.has_index():
            self.collection.create_index(field_name="embedding", index_params=index_params)

        # Load the collection into memory for searching
        self.collection.load()
    
    def create_embedding(self, condition_name: str, condition_short_description: str, condition_long_description: str,condition_calc_pl:str):
        return self.mode.encode(f"{condition_name} {condition_short_description} {condition_long_description} {condition_calc_pl}")
        
    def insert_embedding(self, condition_id:str,condition_symbol:str, condition_name: str, condition_short_description: str, condition_long_description: str,condition_calc_pl:str):
        self.collection.insert([{'condition_id': str(condition_id),'condition_symbol':condition_symbol,'embedding':self.create_embedding(condition_name,condition_short_description,condition_long_description,condition_calc_pl)}])
    
    # Function to find similar conditions based on user input
    def find_similar_conditions(self, user_embedding: List[float], top_k=5):
        # Define search parameters
        search_params = {
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        # Perform the asynchronous search
        search_future = self.collection.search(
            data=[user_embedding],
            anns_field='embedding',
            param=search_params,
            limit=top_k,
            expr=None,
            output_fields=['condition_id','condition_symbol'],
            _async=True  # Ensure the search is asynchronous
        )

        matches = []

        # Wait for the search to complete and get the results
        search_results = search_future.result() # type: ignore

        # Iterate over the SearchResult
        for hits in search_results:
            for hit in hits:
                condition_id = hit.entity.get('condition_id')
                distance = hit.distance
                condition_symbol = hit.entity.get('condition_symbol')
                # Process the hit as needed
                matches.append({'condition_id':condition_id,'similarity_score':distance,'condition_symbol':condition_symbol})
                
        return matches