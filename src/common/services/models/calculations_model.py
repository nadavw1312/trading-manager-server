from pydantic import Field, BaseModel
from typing import Callable, List, Literal, Optional, Dict, Any, TypedDict, Union, Tuple

import polars as pl

from common.base.mongo_base_model import MongoBaseModel

class ParameterField(BaseModel):
    type: str  # e.g., 'int', 'float', 'string'
    range: Optional[Any] = None
    title: str
    description: str

class ReturnsStructureModel(MongoBaseModel):
    type: str
    columns: List[Dict[str, str]]

class CalculationsModel(MongoBaseModel):
    symbol: str = Field(..., description="Unique identifier for the calculation (e.g., 'rsi', 'sma')")
    name: str = Field(..., description="Full name of the calculation (e.g., 'Relative Strength Index')")
    short_description: str = Field(None, description="A brief description of the calculation")
    long_description: str = Field(None, description="Detailed description of what the calculation does")
    trader_usage_example: str = Field(None, description="Example of how traders might use the calculation")
    programmer_usage_example: str = Field(None, description="Example of how to use the calculation in code (e.g., 'rsi.calc(df, params)')")
    returns_structure_of_calc_pl: ReturnsStructureModel = Field(None, description="The structure of the return value from calc_pl")
    params: Dict[str, Any] = Field(None, description="Dynamic parameters used by the calculation (e.g., window size, thresholds)")
    params_fields: Dict[str, ParameterField] = Field(None, description="Metadata about the parameters like data types and valid ranges")
    identifiers: List[str] = Field(None, description="Unique identifiers or keywords related to this calculation")
    category: str = Field(None, description="The category this calculation belongs to (e.g., 'momentum', 'volatility')")
    required_libraries: List[str] = Field(None, description="Any required libraries that this calculation depends on")
    required_calculations: List[str] = Field(None, description="Other calculations required by this calculation (e.g., SMA used by another calculation)")
    plot_type: str = Field(None, description="Defines the type of chart to plot for this calculation (e.g., `'line'`, `'area'`, `'candlestick'`, `'bar'`, `'histogram'`)")
    plot_on: str = Field(None, description="Defines where the plot should be rendered (`'candlestick'` for overlay or `'separate_pane'` for a separate pane)")
    plot_data_format: Dict[str, Any] = Field(None, description="A dictionary including:")
    calc_pl: str = Field(..., description="Python function definition for this calculation")


TimeFrame = Literal['1d', '1h', '15m', '5m', '1m']
class DataFrameByTimeFrames(TypedDict):
    TimeFrame: pl.DataFrame


class CompiledCalc(TypedDict):
    calc_pl: Callable[[DataFrameByTimeFrames, Dict[str, Any]], DataFrameByTimeFrames]
