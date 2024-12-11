import polars as pl
from typing import Dict
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue


TimeFrameDataFrames = Dict[str, pl.DataFrame]

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):  # info is the new argument in Pydantic v2
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError(f"Invalid ObjectId: {v}")
        raise TypeError("ObjectId required")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: JsonSchemaValue, _handler):
        # Customize how the ObjectId will appear in JSON Schema
        schema.update(type="string")
        return schema