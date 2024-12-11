from re import T
from typing import Any, Callable, Dict, Optional, TypeVar
import typing

from pydantic import BaseModel, Field

T = TypeVar("T")

class GeneratedScript:
    name: str
    params: Dict[str, typing.Any]
    calc_pl: Callable

    def __init__(self, name: str, params: Dict[str, object], calc_pl: Callable):
        self.name = name
        self.params = params
        self.calc_pl = calc_pl
        
        
class GlobalResponse(BaseModel, typing.Generic[T]):
    success: bool = Field(..., description="Whether the calculation was successful")
    data: Optional[T] = Field(None, description="The calculated results")
    error: Optional[str] = Field(None, description="Error message if calculation failed")