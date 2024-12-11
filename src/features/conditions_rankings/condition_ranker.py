# import polars as pl
# from conditions.base_condition import BaseCondition
# from enums.types_enums import TimeFrame
# from types import TimeFrameDataFrames
# from abc import ABC, abstractmethod


# class ConditionRanker(ABC):
#     def __init__(self, condition: BaseCondition, dfs: TimeFrameDataFrames):
#         self.condition = condition
#         self.dfs = dfs
#         self.result = None

#     @abstractmethod
#     def main_calculation(self, *kargs,**kwargs) -> pl.Expr:
#         pass

#     def detect_transitions(self, condition_result: pl.Expr) -> pl.Expr:
#         return condition_result & (~condition_result.shift(1).fill_null(False))

#     def rank_condition(self, stock: str):
#         df = self.dfs.get(self.condition)
#         if df is None:
#             print(f"Missing df for stock: {stock}")
#             return

#         df_lazy = df.lazy()

#         condition_result_series = self.condition.evaluate(self.dfs).fill_null(False)
#         condition_result_expr = pl.lit(condition_result_series)

#         transitions_expr = self.detect_transitions(condition_result_expr)
#         main_calculation_expr = self.main_calculation()  # No .sum() here
#         rank_scores_expr = self.rank_conditions_vectorized(transitions_expr, main_calculation_expr)
#         rank_scores_sum_expr = rank_scores_expr.sum()  # Sum the result to get a scalar

#         rank_scores_df = df_lazy.select(rank_scores_sum_expr).collect()
#         rank_scores_scalar = rank_scores_df.item()

#         self.result = {
#             'stock': stock,
#             'condition': self.condition.name,
#             'dynamic_values': self.condition.get_parameters(),
#             'rank_scores': rank_scores_scalar
#         }

#     def rank_conditions_vectorized(self, transitions_expr:pl.Expr,main_calculation_expr:pl.Expr) -> pl.Expr:
#         calc_scaled = pl.when(transitions_expr).then(main_calculation_expr.fill_null(0) * 10).otherwise(0)
#         base_score = pl.when(transitions_expr).then(5).otherwise(0)
#         total_score = base_score + calc_scaled
#         return total_score.sum()
