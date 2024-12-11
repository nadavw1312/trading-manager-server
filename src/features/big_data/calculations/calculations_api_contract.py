from typing import Dict, Any

from pydantic import BaseModel

from common.models import GlobalResponse
from server.src.common.base.model_types import RequestResponseBaseModel

class GetCalculationBySymbolFromToRequest(RequestResponseBaseModel):
    calculation_symbol: str
    calculation_params: Dict[str, Any]  # Specify the correct types here
    from_date: str
    to_date: str
    stock_symbol: str

class GetCalculationBySymbolFromToResponse(GlobalResponse[Dict[str, Any]]):
    pass

