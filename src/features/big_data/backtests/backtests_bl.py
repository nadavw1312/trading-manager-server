
from common.base.base_mongo_bl import BaseMongoBl
from features.big_data.backtests.backtests_dal import BackTestsDal
from server.src.common.services.models.backtests_model import BackTestsModel

class BackTestsBl(BaseMongoBl[BackTestsDal, BackTestsModel]):
    def __init__(self):
        super().__init__(BackTestsDal)
