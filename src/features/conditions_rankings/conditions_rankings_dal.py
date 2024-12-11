# # db_collections/ranking_collection.py
# from db_collections.base_mongo_dal import BaseMongoDal
# from pymongo import ASCENDING

# class ConditionsRankingDal(BaseMongoDal):
#     def __init__(self):
#         super().__init__('rankings')

#     def find_top_rankings(self, limit: int = 10) -> list:
#         return list(self.collection.find({}).sort("score", ASCENDING).limit(limit))

#     def update_ranking_score(self, condition_name: str, new_score: float) -> dict:
#         return self.update_one({"condition_name": condition_name}, {"score": new_score})
