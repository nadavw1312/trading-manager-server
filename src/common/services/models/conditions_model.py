from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from bson import ObjectId

from common.base.mongo_base_model import MongoBaseModel



class ConditionsModel(MongoBaseModel):
    symbol: str = Field(..., description="Unique identifier for the condition (e.g., 'sma_cross', 'rsi_obos')")
    name: str = Field(..., description="Full name of the condition (e.g., 'SMA Crossover', 'RSI Overbought/Oversold')")
    short_description: str = Field(..., description="Brief explanation of the condition and its purpose")
    long_description: str = Field(..., description="Detailed explanation of the condition and its logic")
    trader_usage_example: str = Field(..., description="A human-friendly use case explaining how to apply this condition for trading decisions")
    programmer_usage_example: str = Field(..., description="A code example for how to use the condition (e.g., 'SmaCross.calc(df, params)')")
    is_only_exit: bool = Field(False, description="Boolean to indicate if this condition can only be used for exit signals")
    actions: Optional[List[str]] = Field(None, description="Actions that this condition can perform (e.g., 'cross above', 'greater than')")
    logical_operators: Optional[List[str]] = Field(None, description="Logical operators that this condition can use (e.g., 'and', 'or', 'not')")
    params: Dict[str, Any] = Field(..., description="Dynamic parameters used by the condition (e.g., timeframes, thresholds)")
    params_fields: Dict[str, Dict[str, Any]] = Field(..., description="Metadata about the parameters like data types and valid ranges")
    identifiers: List[str] = Field(..., description="Unique identifiers or keywords related to this condition, such as used columns")
    category: str = Field(..., description="The category this condition belongs to (e.g., 'trend', 'momentum')")
    required_libraries: List[str] = Field(..., description="Any required libraries that this condition depends on")
    required_calculations: List[str] = Field(..., description="Other calculations required by this condition (e.g., 'Sma', 'Rsi')")
    calc_pl: str = Field(..., description="Python class definition for this condition")
    embedding: Optional[List[float]] = Field(None, description="Embedding to find and validate conditions")
