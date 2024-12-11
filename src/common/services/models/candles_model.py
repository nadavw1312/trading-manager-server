from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime as dt
from typing import Optional
from common.base.mongo_base_model import MongoBaseModel
from common.types import PydanticObjectId

class CandleModel(MongoBaseModel):
    stock_id: ObjectId = Field(..., description="The ID of the stock")
    stock_name: str = Field(..., description="The name of the stock")
    datetime: dt = Field(..., description="The datetime of the candle data")
    date: dt = Field(..., description="The date of the candle data")
    open: float = Field(..., description="The opening price")
    high: float = Field(..., description="The highest price")
    low: float = Field(..., description="The lowest price")
    close: float = Field(..., description="The closing price")
    volume: float = Field(..., description="The trading volume")
    timeframe: str = Field(..., description="The timeframe of the candle (e.g., '1m', '5m', '1h')")

class CandleStickModel(BaseModel):
    datetime: dt = Field(..., description="The date of the candle data")
    open: float = Field(..., description="The opening price")
    high: float = Field(..., description="The highest price")
    low: float = Field(..., description="The lowest price")
    close: float = Field(..., description="The closing price")
