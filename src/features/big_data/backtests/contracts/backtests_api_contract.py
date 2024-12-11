import datetime
from typing import Any, Dict, List, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from server.src.common.base.model_types import RequestResponseBaseModel, to_camel

class BackTestCondition(RequestResponseBaseModel):
    symbol: str
    params: Dict[str, Any]

class BackTestRequest(RequestResponseBaseModel):
    tickers: List[str]
    from_datetime: str
    to_datetime: str
    entry_conditions: List[BackTestCondition]
    exit_conditions: List[BackTestCondition]
    type: Literal['first_daily_trade', 'each_day']

class BackTestPosition(BaseModel):
    position_id: int
    Date: datetime.datetime = Field(alias="date")
    entry_index: int
    exit_index: int
    entry_time: datetime.datetime
    exit_time: datetime.datetime
    entry_price: float
    exit_price: float
    profit: float
    
    class Config:
        alias_generator = to_camel
        populate_by_name = True
    

class BackTestResponse(RequestResponseBaseModel):
    positions: Dict[str, List[BackTestPosition]]
