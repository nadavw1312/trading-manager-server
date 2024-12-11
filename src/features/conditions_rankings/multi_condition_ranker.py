# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import List, Type
# from server.src.common.types import TimeFrameDataFrames


# class MultiConditionRanker:
#     def __init__(self, conditions: List[BaseCondition], stock_dfs: TimeFrameDataFrames, ranker_class: Type[ConditionRanker]):
#         self.conditions = conditions
#         self.stock_dfs = stock_dfs
#         self.ranker_class = ranker_class  # Accept a ConditionRanker class
#         self.results = []

#     def evaluate_conditions(self, stock: str):
#         # Use ThreadPoolExecutor to evaluate each condition in parallel
#         with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
#             futures = [executor.submit(self._rank_single_condition, condition, stock) for condition in self.conditions]
            
#             for future in as_completed(futures):
#                 try:
#                     result = future.result()
#                     if result:
#                         self.results.append(result)
#                 except Exception as e:
#                     print(f"Error evaluating condition: {e}")

#     def _rank_single_condition(self, condition: BaseCondition, stock: str):
#         # Create a ConditionRanker (or its subclass) for each condition and evaluate it
#         ranker = self.ranker_class(condition, self.stock_dfs, condition.timeframe)  # Use the specified ranker class
#         ranker.rank_condition(stock)
#         return ranker.result

#     def get_ranked_results(self):
#         ranked_results = sorted(
#             self.results, 
#             key=lambda x: x['rank_scores'],  # Higher score is better
#             reverse=True
#         )
#         return ranked_results
