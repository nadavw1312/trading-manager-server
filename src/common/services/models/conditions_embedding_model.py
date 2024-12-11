from pydantic import BaseModel


class ConditionEmbeddingModel(BaseModel):
    id:str
    symbol:str
    condition_id:str
    embedding:str