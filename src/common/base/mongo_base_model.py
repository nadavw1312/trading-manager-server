from typing import Optional, TypeVar
from bson import ObjectId

from pydantic import BaseModel, Field

from server.src.common.types import PydanticObjectId


# Helper function to convert snake_case to camelCase
def to_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# MongoBaseModel with camelCase conversion
class MongoBaseModel(BaseModel):
    id: Optional[PydanticObjectId] = Field(default=None, description="Unique identifier", alias='_id')  # type: ignore
    
    class Config:
        # Use the alias generator for camelCase conversion
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        validate_assignment = True
        extra = 'allow'


T_Model = TypeVar('T_Model', bound=MongoBaseModel)
