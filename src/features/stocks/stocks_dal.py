from common.base.base_mongo_dal import BaseMongoDal
from common.services.models.stock_model import StockModel
from pymongo import ASCENDING

from server.src.common.utils.singleton import singleton

COLLECTION_NAME = "stocks"

@singleton
class StocksDal(BaseMongoDal[StockModel]):
    def __init__(self):
        super().__init__(collection_name=COLLECTION_NAME, data_class=StockModel)
        self.collection.create_index([("ticker", ASCENDING)], unique=True)  # Ensure ticker is unique

    def get_stock_by_ticker(self, ticker: str) -> StockModel:
        """
        Retrieves a stock by its ticker symbol.
        Returns a Stock object.
        """
        return self.find_one({"ticker": ticker})

    def get_stock_by_name(self, name: str) -> list[StockModel]:
        """
        Retrieves stocks with a similar name.
        Returns a list of Stock objects.
        """
        return self.find({"name": {"$regex": name, "$options": "i"}})

    def get_all_stocks(self) -> list[StockModel]:
        """
        Retrieves all stocks in the collection.
        Returns a list of Stock objects.
        """
        return self.find({})
