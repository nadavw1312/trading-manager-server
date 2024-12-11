
from pymongo import ASCENDING
from common.base.base_mongo_dal import BaseMongoDal
from common.services.models.backtests_model import BackTestsModel
from server.src.common.utils.singleton import singleton

COLLECTION_NAME = "backtests"

@singleton
class BackTestsDal(BaseMongoDal[BackTestsModel]):
    def __init__(self):
        super().__init__(collection_name="backtests", data_class=BackTestsModel)
        # Ensure the combination of 'ticker', 'from_datetime', 'to_datetime', 'entry_conditions_id', and 'exit_conditions_id' is unique
        self.collection.create_index(
            [
                ("ticker", ASCENDING),
                ("from_datetime", ASCENDING),
                ("to_datetime", ASCENDING),
                ("entry_conditions_id", ASCENDING),
                ("exit_conditions_id", ASCENDING),
            ],
            unique=True,
        )

    def get_backtest_by_ticker(self, ticker: str) -> BackTestsModel:
        """
        Retrieves a backtest by its unique ticker.
        Returns a BackTestsModel object.
        """
        return self.find_one({"ticker": ticker})

    def get_all_backtests(self) -> list[BackTestsModel]:
        """
        Retrieves all backtests in the collection.
        Returns a list of BackTestsModel objects.
        """
        return self.find({})

    def update_backtest(self, ticker: str, update_data: dict) -> dict:
        """
        Updates a backtest by its ticker.
        Returns the matched and modified count.
        """
        return self.update_one({"ticker": ticker}, update_data)

    def delete_backtest(self, ticker: str) -> dict:
        """
        Deletes a backtest by its ticker.
        Returns the count of deleted documents.
        """
        return self.delete_one({"ticker": ticker})