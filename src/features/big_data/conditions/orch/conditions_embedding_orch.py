from typing import List, TypedDict

from pydantic import BaseModel
from server.src.features.big_data.conditions.bl.conditions_embedding_bl import ConditionsEmbeddingBl
from server.src.features.big_data.conditions.conditions_bl import ConditionsBl
from server.src.features.big_data.conditions.conditions_orch import ConditionsOrch

class ConditionsEmbeddingOrch:
    def __init__(self):
        self.bl = ConditionsEmbeddingBl()
        self.conditions_bl = ConditionsBl()
    
    def insert_conditions_embeddings(self):
        conditions = self.conditions_bl.find_all()
        for cond in conditions:
            self.bl.insert_embedding(**cond.model_dump())
    
    
    def find_similar_conditions(self, user_embedding: List[float], top_k=5):
        return self.bl.find_similar_conditions(user_embedding,top_k)