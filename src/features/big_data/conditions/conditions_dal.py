
import logging
from pymongo import ASCENDING
from common.base.base_mongo_dal import BaseMongoDal
from common.services.models.conditions_model import ConditionsModel
from server.src.common.utils.singleton import singleton
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLLECTION_NAME = "conditions"

@singleton
class ConditionsDal(BaseMongoDal[ConditionsModel]):
    def __init__(self):
        super().__init__(collection_name=COLLECTION_NAME, data_class=ConditionsModel)
        # Ensure 'symbol' is unique
        self.collection.create_index([("symbol", ASCENDING)], unique=True)
        # Ensure the embedding field is indexed for vector search
        self.collection.create_index([('embedding', ASCENDING)])


    def get_by_symbol(self, symbol: str):
        """ Retrieves a condition by its unique symbol (e.g., 'ma_cross'). """
        return self.find_one({"symbol": symbol})

    def get_by_name(self, name: str):
        """ Retrieves conditions with a similar name. """
        return self.find({"name": {"$regex": name, "$options": "i"}})
    
    def get_by_symbols(self, symbols: list[str]):
        """ Retrieves conditions that match any of the provided names. """
        return self.find({"symbol": {"$in": symbols}})

    def get_all(self) -> list[ConditionsModel]:
        """ Retrieves all conditions in the collection. """
        return self.find({})

    def update(self, symbol: str, update_data: dict):
        """ Updates a condition by its symbol. """
        return self.update_one({"symbol": symbol}, update_data)

    def delete(self, symbol: str):
        """ Deletes a condition by its symbol. """
        return self.delete_one({"symbol": symbol})

    def get_by_indicators_and_action(self, indicators: list[str], actions: list[str]):
        """
        Retrieves conditions that match a list of indicators and actions.
        Performs a regex search for conditions that have matching indicators (identifiers)
        and similar descriptions (long_description, short_description) for actions.
        """
        indicator_query = '|'.join(indicators)  # Create a regex OR query for indicators
        action_query = '|'.join(actions)        # Create a regex OR query for actions
        
        return self.find({
            "$or": [
                {"identifiers": {"$regex": indicator_query, "$options": "i"}},
                {"long_description": {"$regex": action_query, "$options": "i"}},
                {"short_description": {"$regex": action_query, "$options": "i"}}
            ]
        })
    
    def find_similar_conditions(self, embedding, top_k=5):
        """Find conditions similar to the given embedding using vector search."""
        try:
            pipeline = [
                {
                    '$search': {
                        'knnBeta': {
                            'vector': embedding,
                            'path': 'embedding',
                            'k': top_k
                        }
                    }
                },
                {
                    '$project': {
                        'name': 1,
                        'description': 1,
                        'embedding': 1,
                        '_id': 0,
                        'score': {'$meta': 'searchScore'}
                    }
                }
            ]
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            logger.error("Error performing vector search: %s", e)
            return []

    def update_condition_embeddings(self,condition_id,embedding):
        """
        Update all existing conditions with embeddings.
        """

        self.collection.update_one(
            {'_id': condition_id},
                {'$set': {'embedding': embedding}}
        )
        logger.info("Updated condition '%s' with embedding.", condition_id)
    