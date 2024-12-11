from typing import List, TypedDict

class ConditionEmbeddingDict(TypedDict):
    condition_id: str
    embedding: List[float]