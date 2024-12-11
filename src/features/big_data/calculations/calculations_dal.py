from typing import Any
from pymongo import ASCENDING
from common.base.base_mongo_dal import BaseMongoDal
from common.services.models.calculations_model import CalculationsModel
from server.src.common.utils.singleton import singleton

COLLECTION_NAME = "calculations"

@singleton
class CalculationsDal(BaseMongoDal[CalculationsModel]):
    def __init__(self):
        super().__init__(collection_name="calculations", data_class=CalculationsModel)
        # Ensure 'symbol' is unique
        self.collection.create_index([("symbol", ASCENDING)], unique=True)

    def get_calculation_by_symbol(self, symbol: str) -> CalculationsModel:
        """
        Retrieves a calculation by its unique symbol (e.g., 'rsi', 'sma').
        Returns a Calculation object.
        """
        return self.find({"symbol": symbol.lower()})[0]

    def get_calculations_by_name(self, name: str) -> list[CalculationsModel]:
        """
        Retrieves calculations with a similar name.
        Returns a list of Calculation objects.
        """
        return self.find({"name": {"$regex": name, "$options": "i"}})

    def get_all_calculations(self) -> list[CalculationsModel]:
        """
        Retrieves all calculations in the collection.
        Returns a list of Calculation objects.
        """
        return self.find_all()

    def update_calculation(self, symbol: str, update_data: dict[str, Any]):
        """
        Updates a calculation by its symbol.
        Returns the matched and modified count.
        """
        return self.update_one({"symbol": symbol}, update_data)

    def delete_calculation(self, symbol: str) -> dict:
        """
        Deletes a calculation by its symbol.
        Returns the count of deleted documents.
        """
        return self.delete_one({"symbol": symbol})

    def get_all_symbols(self) -> list[str]:
        # Extract the 'symbol' field from each CalculationsModel object
        return [calculation['symbol'] for calculation in self.collection.find({}, projection={"symbol": 1})]

