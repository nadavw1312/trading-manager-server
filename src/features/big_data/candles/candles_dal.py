from datetime import date, datetime
from common.base.base_mongo_dal import BaseMongoDal


from pymongo import ASCENDING

from server.src.common.services.models.candles_model import CandleModel
from server.src.common.utils.singleton import singleton

COLLECTION_NAME = "candles"

@singleton
class CandlesDal(BaseMongoDal[CandleModel]):
    def __init__(self):
        super().__init__(collection_name=COLLECTION_NAME, data_class=CandleModel)
        self.collection.create_index([("stockName", ASCENDING), ("datetime", ASCENDING), ("timeframe", ASCENDING)], unique=True)

    def get_candles_by_stock(self, stock_name: str, start_date: date, end_date: date, timeframe: str) -> list[CandleModel]:
        """
        Retrieves candles for a specific stock by stockId, timeframe, and date range.
        Returns a list of Candle objects.
        """
        query = {
            "stockName": stock_name,
            "timeframe": timeframe,
            "datetime": {"$gte": datetime.strptime(start_date.strftime('%Y-%m-%d'), '%Y-%m-%d'), "$lte": datetime.strptime(end_date.strftime('%Y-%m-%d'), '%Y-%m-%d')}
        }
        return self.find(query)

    def get_latest_candle(self, stock_id: str, timeframe: str):
        """
        Retrieves the most recent candle for a stock in a specific timeframe.
        Returns a Candle object.
        """
        query = {"stockId": stock_id, "timeframe": timeframe}
        return self.find(query)  # Sort by date descending

    def delete_candles_by_stock(self, stock_id: str, timeframe: str):
        """
        Deletes all candles for a specific stock and timeframe.
        Returns the number of deleted documents.
        """
        return self.delete_many({"stockId": stock_id, "timeframe": timeframe})
