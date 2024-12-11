from typing import List
from server.src.features.big_data.conditions.dal.conditions_embedding_dal import ConditionsEmbeddingDal


class ConditionsEmbeddingBl:
    def __init__(self):
        self.dal = ConditionsEmbeddingDal()
        
            
    def insert_embedding(self, id:str, symbol: str,name: str ,short_description: str, long_description: str,calc_pl:str,**kwargs):
        return self.dal.insert_embedding(id,symbol,name,short_description,long_description,calc_pl)


    def find_similar_conditions(self, user_embedding: List[float], top_k=5):
        return self.dal.find_similar_conditions(user_embedding,top_k)