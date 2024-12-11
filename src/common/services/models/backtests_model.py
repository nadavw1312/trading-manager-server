from pydantic import Field
from typing import Optional
from server.src.common.base.mongo_base_model import MongoBaseModel
from server.src.common.types import PydanticObjectId


class BackTestsModel(MongoBaseModel):
    ticker: str = Field(..., description="BackTest ticker symbol")
    from_datetime: str = Field(..., description="Start date of the backtest") 
    to_datetime: str = Field(..., description="End date of the backtest")
    entry_conditions: list[str] = Field(..., description="List of entry conditions")
    entry_conditions_id: str = Field(..., description="string of entry conditions symbol sorted by abc and combined by -")
    exit_conditions: list[str] = Field(..., description="List of exit conditions")
    exit_conditions_id: str = Field(..., description="string of exit conditions symbol sorted by abc and combined by -")
    trades: list[str] = Field(..., description="List of trades executed during the backtest")
    profit: float = Field(..., description="Total profit earned during the backtest")