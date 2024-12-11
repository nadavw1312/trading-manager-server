# import polars as pl
# from conditions.base_condition import BaseCondition
# from enums.types_enums import TimeFrame
# from big_data.features.conditions_rankings.condition_ranker import ConditionRanker
# from types import TimeFrameDataFrames


# class MomentumRanker(ConditionRanker):
#     def main_calculation(self, lookback_period: int = 5) -> pl.Expr:
#         return (pl.col('Close') - pl.col('Close').shift(lookback_period)) / pl.col('Close').shift(lookback_period).fill_null(0)

