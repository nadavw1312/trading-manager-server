from pydantic import Field
from typing import Optional
from common.base.mongo_base_model import MongoBaseModel
from common.types import PydanticObjectId



class StockModel(MongoBaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    short_name: Optional[str] = Field(None, description="Short name of the stock")
    long_name: Optional[str] = Field(None, description="Long name of the company")
    sector: Optional[str] = Field(None, description="Business sector of the company")
    industry: Optional[str] = Field(None, description="Industry in which the company operates")
    market_cap: Optional[int] = Field(None, description="Market capitalization of the company")
    website: Optional[str] = Field(None, description="Official website of the company")
    country: Optional[str] = Field(None, description="Country where the company is based")
    currency: Optional[str] = Field(None, description="Currency in which the stock is traded")
    description: Optional[str] = Field(None, description="Detailed business summary of the company")
    CEO: Optional[str] = Field(None, description="CEO of the company")
    employees: Optional[int] = Field(None, description="Number of full-time employees")
    headquarters: Optional[str] = Field(None, description="Location of the company's headquarters")
