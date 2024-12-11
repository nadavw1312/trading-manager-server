from pydantic import BaseModel


class GetCandlesByTickerFromToRequest(BaseModel):
    from_date: str
    to_date: str
    stock_name: str
    timeframe: str